"""
AlertaService — geração e gestão de alertas.

REGRAS DE GERAÇÃO (chamadas pelo scheduler ou manualmente):

  Vencimento:
    - 30 dias antes da validade → ALERTA_30_DIAS
    - 15 dias antes da validade → ALERTA_15_DIAS  (escala o alerta existente)
    -  7 dias antes da validade → ALERTA_7_DIAS   (escala o alerta existente)
    Só gera se o lote ainda tem saldo > 0.

  Estoque crítico:
    Dispara quando QUALQUER condição for verdadeira:
      a) saldo_atual <= medicamento.estoque_minimo        (limiar absoluto)
      b) saldo_atual <= quantidade_inicial_lote * 0.10   (limiar relativo — 10%)
    A condição (b) captura lotes de alto volume onde o mínimo absoluto
    ainda não foi atingido mas o consumo já é preocupante.

REGRAS DE STATUS:
    PENDENTE    → estado inicial de todo alerta gerado
    EM_ANDAMENTO → operador reconheceu e está tratando
    RESOLVIDO   → problema corrigido (novo lote chegou, lote descartado, etc.)
    EXPIRADO    → alerta de vencimento cujo lote já venceu sem ação

IDEMPOTÊNCIA:
    O scheduler roda diariamente. Antes de criar um alerta, o service
    verifica se já existe um alerta PENDENTE ou EM_ANDAMENTO do mesmo
    tipo para o mesmo lote — evita duplicatas.

ESCALADA:
    Quando um lote passa de 30 para 15 dias de validade, o alerta de
    30 dias é marcado como EXPIRADO e um novo de 15 dias é criado.
    Isso garante que o painel sempre mostre o alerta mais urgente.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.alertas.model import Alertas, StatusAlerta, TipoAlerta
from app.core.exceptions import RecursoNaoEncontrado, RegraDeNegocioViolada
from app.lote.model import Lote
from app.medicamentos.model import Medicamento


# Limiares de vencimento em dias
LIMIARES_VENCIMENTO = [
    (7,  TipoAlerta.ALERTA_7_DIAS),
    (15, TipoAlerta.ALERTA_15_DIAS),
    (30, TipoAlerta.ALERTA_30_DIAS),
]

# Percentual de estoque para alerta relativo
PERCENTUAL_CRITICO = 0.10


class AlertaService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ── Geração de alertas (chamada pelo scheduler) ───────────────────────────

    async def verificar_todos(self) -> dict:
        """
        Verifica todos os lotes ativos e gera alertas necessários.

        Chamado pelo APScheduler diariamente à meia-noite.
        Também pode ser chamado manualmente via POST /alertas/verificar.

        Returns:
            Sumário com contagem de alertas criados, escalados e expirados.
        """
        criados   = 0
        escalados = 0
        expirados = 0
        hoje = date.today()

        # Carrega todos os lotes com saldo > 0, junto com o medicamento
        lotes = await self._lotes_ativos()

        for lote in lotes:
            med = lote.medicamento

            # ── Alertas de vencimento ────────────────────────────────────────
            dias_restantes = (lote.validade - hoje).days

            if dias_restantes < 0:
                # Lote já vencido — expira alertas abertos
                n = await self._expirar_alertas_vencimento(lote.id)
                expirados += n
                continue

            # Determina qual limiar se aplica hoje
            tipo_atual = None
            for (dias, tipo) in LIMIARES_VENCIMENTO:  # ordem: 7, 15, 30
                if dias_restantes <= dias:
                    tipo_atual = tipo
                    break

            if tipo_atual:
                resultado = await self._gerar_ou_escalar_vencimento(lote, tipo_atual)
                criados   += resultado["criados"]
                escalados += resultado["escalados"]

            # ── Alerta de estoque crítico ────────────────────────────────────
            if self._estoque_critico(lote, med):
                foi_criado = await self._gerar_estoque_critico(lote, med)
                criados += 1 if foi_criado else 0

        await self.session.flush()

        return {
            "data_verificacao": hoje.isoformat(),
            "alertas_criados":   criados,
            "alertas_escalados": escalados,
            "alertas_expirados": expirados,
        }

    # ── Leitura de alertas ────────────────────────────────────────────────────

    async def listar(
        self,
        status: StatusAlerta | None = None,
        tipo: TipoAlerta | None = None,
        medicamento_id: str | None = None,
        apenas_ativos: bool = True,
    ) -> list[Alertas]:
        """
        Lista alertas com filtros opcionais.

        Args:
            status:         Filtra por status (None = todos).
            tipo:           Filtra por tipo de alerta.
            medicamento_id: Filtra por medicamento.
            apenas_ativos:  Se True, exclui RESOLVIDO e EXPIRADO.
        """
        stmt = (
            select(Alertas)
            .options(
                selectinload(Alertas.lote),
                selectinload(Alertas.medicamento),
            )
            .order_by(Alertas.gerado_em.desc())
        )

        if status:
            stmt = stmt.where(Alertas.status == status)
        elif apenas_ativos:
            stmt = stmt.where(
                Alertas.status.in_([StatusAlerta.PENDENTE, StatusAlerta.EM_ANDAMENTO])
            )

        if tipo:
            stmt = stmt.where(Alertas.tipo == tipo)

        if medicamento_id:
            stmt = stmt.where(Alertas.medicamento_id == medicamento_id)

        resultado = await self.session.execute(stmt)
        return list(resultado.scalars().all())

    async def buscar_por_id(self, alerta_id: str) -> Alertas:
        resultado = await self.session.execute(
            select(Alertas)
            .options(
                selectinload(Alertas.lote),
                selectinload(Alertas.medicamento),
            )
            .where(Alertas.id == alerta_id)
        )
        alerta = resultado.scalar_one_or_none()
        if not alerta:
            raise RecursoNaoEncontrado("Alerta", alerta_id)
        return alerta

    # ── Atualização de status (ação do operador) ──────────────────────────────

    async def atualizar_status(
        self,
        alerta_id: str,
        novo_status: StatusAlerta,
        usuario_id: str,
    ) -> Alertas:
        """
        Atualiza o status de um alerta seguindo a máquina de estados.

        Transições permitidas:
            PENDENTE     → EM_ANDAMENTO, RESOLVIDO
            EM_ANDAMENTO → RESOLVIDO
            RESOLVIDO    → (nenhuma — estado terminal)
            EXPIRADO     → (nenhuma — estado terminal)

        Args:
            alerta_id:   UUID do alerta.
            novo_status: Status desejado.
            usuario_id:  ID do usuário que está fazendo a transição (para log futuro).

        Raises:
            RegraDeNegocioViolada: Transição de status inválida.
        """
        alerta = await self.buscar_por_id(alerta_id)

        self._validar_transicao(alerta.status, novo_status)

        alerta.status = novo_status
        if novo_status == StatusAlerta.RESOLVIDO:
            alerta.resolvido_em = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(alerta)
        return alerta

    # ── Privados ──────────────────────────────────────────────────────────────

    async def _lotes_ativos(self) -> list[Lote]:
        """Retorna lotes com saldo > 0 e medicamento carregado."""
        resultado = await self.session.execute(
            select(Lote)
            .options(selectinload(Lote.medicamento))
            .where(Lote.quantidade_atual > 0)
        )
        return list(resultado.scalars().all())

    async def _gerar_ou_escalar_vencimento(
        self, lote: Lote, tipo_atual: TipoAlerta
    ) -> dict:
        """
        Gera um novo alerta de vencimento ou escala o existente.

        Escalada: ALERTA_30_DIAS → ALERTA_15_DIAS → ALERTA_7_DIAS.
        Quando o limiar muda, o alerta anterior é EXPIRADO e um novo
        é criado com o tipo mais urgente.
        """
        criados = escalados = 0

        # Busca alerta aberto de vencimento para este lote
        alerta_existente = await self._alerta_aberto_vencimento(lote.id)

        if alerta_existente:
            if alerta_existente.tipo == tipo_atual:
                # Mesmo limiar — nada a fazer
                return {"criados": 0, "escalados": 0}
            else:
                # Limiar mudou — expira o antigo e cria o novo
                alerta_existente.status = StatusAlerta.EXPIRADO
                escalados += 1

        self.session.add(Alertas(
            lote_id        = lote.id,
            medicamento_id = lote.medicamento_id,
            tipo           = tipo_atual,
            status         = StatusAlerta.PENDENTE,
        ))
        criados += 1

        return {"criados": criados, "escalados": escalados}

    async def _gerar_estoque_critico(self, lote: Lote, med: Medicamento) -> bool:
        """
        Gera alerta de estoque crítico se não houver um aberto.
        Retorna True se criou, False se já existia.
        """
        existe = await self.session.execute(
            select(Alertas).where(
                and_(
                    Alertas.lote_id == lote.id,
                    Alertas.tipo   == TipoAlerta.ALERTA_ESTOQUE_CRITICO,
                    Alertas.status.in_([StatusAlerta.PENDENTE, StatusAlerta.EM_ANDAMENTO]),
                )
            )
        )
        if existe.scalar_one_or_none():
            return False

        self.session.add(Alertas(
            lote_id        = lote.id,
            medicamento_id = lote.medicamento_id,
            tipo           = TipoAlerta.ALERTA_ESTOQUE_CRITICO,
            status         = StatusAlerta.PENDENTE,
        ))
        return True

    async def _alerta_aberto_vencimento(self, lote_id: str) -> Alertas | None:
        """Retorna o alerta de vencimento aberto (PENDENTE ou EM_ANDAMENTO) do lote."""
        resultado = await self.session.execute(
            select(Alertas).where(
                and_(
                    Alertas.lote_id == lote_id,
                    Alertas.tipo.in_([
                        TipoAlerta.ALERTA_30_DIAS,
                        TipoAlerta.ALERTA_15_DIAS,
                        TipoAlerta.ALERTA_7_DIAS,
                    ]),
                    Alertas.status.in_([StatusAlerta.PENDENTE, StatusAlerta.EM_ANDAMENTO]),
                )
            )
        )
        return resultado.scalar_one_or_none()

    async def _expirar_alertas_vencimento(self, lote_id: str) -> int:
        """Expira todos os alertas de vencimento abertos de um lote vencido."""
        resultado = await self.session.execute(
            select(Alertas).where(
                and_(
                    Alertas.lote_id == lote_id,
                    Alertas.tipo.in_([
                        TipoAlerta.ALERTA_30_DIAS,
                        TipoAlerta.ALERTA_15_DIAS,
                        TipoAlerta.ALERTA_7_DIAS,
                    ]),
                    Alertas.status.in_([StatusAlerta.PENDENTE, StatusAlerta.EM_ANDAMENTO]),
                )
            )
        )
        alertas = list(resultado.scalars().all())
        for a in alertas:
            a.status = StatusAlerta.EXPIRADO
        return len(alertas)

    @staticmethod
    def _estoque_critico(lote: Lote, med: Medicamento) -> bool:
        """
        Retorna True se o saldo atual atingiu o limiar crítico.

        Condição composta (OR):
          a) Limiar absoluto: saldo <= estoque_minimo do medicamento
          b) Limiar relativo: saldo <= 10% da quantidade inicial do lote
        """
        limiar_absoluto = lote.quantidade_atual <= med.estoque_minimo
        limiar_relativo = lote.quantidade_atual <= lote.quantidade_inicial * PERCENTUAL_CRITICO
        return limiar_absoluto or limiar_relativo

    @staticmethod
    def _validar_transicao(atual: StatusAlerta, novo: StatusAlerta) -> None:
        """Aplica a máquina de estados do alerta."""
        TRANSICOES_PERMITIDAS: dict[StatusAlerta, set[StatusAlerta]] = {
            StatusAlerta.PENDENTE:     {StatusAlerta.EM_ANDAMENTO, StatusAlerta.RESOLVIDO},
            StatusAlerta.EM_ANDAMENTO: {StatusAlerta.RESOLVIDO},
            StatusAlerta.RESOLVIDO:    set(),
            StatusAlerta.EXPIRADO:     set(),
        }
        permitidos = TRANSICOES_PERMITIDAS.get(atual, set())
        if novo not in permitidos:
            destinos = ", ".join(s.value for s in permitidos) or "nenhum"
            raise RegraDeNegocioViolada(
                f"Transição inválida: '{atual.value}' → '{novo.value}'. "
                f"Transições permitidas a partir de '{atual.value}': {destinos}."
            )
