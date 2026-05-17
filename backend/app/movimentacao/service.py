"""
Service de movimentacao — regras de negócio.

PADRÃO DO PROJETO — regras do service:
  - Orquestra repositórios. Nunca acessa self.session.execute() diretamente.
  - Contém TODA a lógica de negócio (validações, decisões, cálculos).
  - Levanta exceções de domínio (app.core.exceptions).
  - É a camada testada nos testes unitários (sem banco real).
"""
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado, EstoqueInsuficiente, RegraDeNegocioViolada
from app.lote.model import Lote
from app.movimentacao.model import Movimentacao, TipoMovimentacao
from app.movimentacao.repository import MovimentacaoRepository
from app.movimentacao.schema import MovimentacaoCreate, MovimentacaoUpdate


class MovimentacaoService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MovimentacaoRepository(session)

    async def criar(self, dados: MovimentacaoCreate) -> Movimentacao:
        """
        Cria o registro histórico de uma movimentação, atualizando o saldo do lote.

        Regras de negócio:
        - Para SAÍDA: verifica se o lote tem saldo suficiente (raise EstoqueInsuficiente).
        - Para ENTRADA: se o lote estiver vencido, exige justificativa (raise RegraDeNegocioViolada).
        - O saldo do lote é atualizado atomica e consistentemente, evitando condições de corrida.
        """

        resultado = await self.session.execute(
            select(Lote)
            .where(Lote.id == dados.lote_id)
            .with_for_update()          # trava até o commit/rollback da transação
        )
        lote = resultado.scalar_one_or_none()

        if not lote:
            raise RecursoNaoEncontrado("Lote", dados.lote_id)

        await self._validar(dados, lote)

        lote.quantidade_atual = self._novo_saldo(lote.quantidade_atual, dados)

        mov = Movimentacao(
            lote_id       = lote.id,
            usuario_id    = dados.usuario_id,
            tipo          = dados.tipo,
            quantidade    = dados.quantidade,
            justificativa = dados.justificativa,
            ocorrido_em   = datetime.now(timezone.utc),
        )
        self.session.add(mov)

        # flush persiste no banco mas ainda dentro da transação —
        # o commit é responsabilidade do get_session() em core/dependencies.py
        await self.session.flush()
        await self.session.refresh(mov)

        return mov

    async def buscar_por_id(self, movimentacao_id: str) -> Movimentacao:
        """
        Retorna uma movimentação pelo ID.

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
        """
        movimentacao = await self.repo.get_by_id(movimentacao_id)
        if not movimentacao:
            raise RecursoNaoEncontrado("Movimentação", movimentacao_id)
        return movimentacao

    async def listar(self, lote_id: str | None = None) -> list[Movimentacao]:
        """
        Lista movimentações, opcionalmente filtrando por um lote específico.
        """
        return await self.repo.list_all(lote_id=lote_id)

    async def atualizar(self, movimentacao_id: str, dados: MovimentacaoUpdate) -> Movimentacao:
        """
        Atualiza parcialmente uma movimentação.
        Em regras de estoque, geralmente atualiza-se apenas a justificativa.

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
        """
        movimentacao = await self.buscar_por_id(movimentacao_id)
        campos = dados.model_dump(exclude_unset=True)
        return await self.repo.update(movimentacao, campos)
    
    @staticmethod
    def _novo_saldo(saldo_atual: int, dados: MovimentacaoCreate) -> int:
        """Calcula e valida o novo saldo após a movimentação."""
        if dados.tipo == TipoMovimentacao.ENTRADA:
            return saldo_atual + dados.quantidade

        # Saídas: DISPENSACAO, PERDA, AJUSTE negativo
        novo = saldo_atual - dados.quantidade
        if novo < 0:
            raise EstoqueInsuficiente(
                lote_id    = dados.lote_id,
                disponivel = saldo_atual,
                solicitado = dados.quantidade,
            )
        return novo

    @staticmethod
    async def _validar(dados: MovimentacaoCreate, lote: Lote) -> None:
        """Aplica regras de negócio antes de qualquer escrita."""
        from datetime import date

        # Ajuste e perda exigem justificativa (requisito do briefing)
        if dados.tipo in (TipoMovimentacao.AJUSTE, TipoMovimentacao.PERDA):
            if not dados.justificativa or not dados.justificativa.strip():
                raise RegraDeNegocioViolada(
                    f"Justificativa é obrigatória para movimentações do tipo '{dados.tipo.value}'."
                )

        # Não permite entrada em lote vencido
        if dados.tipo == TipoMovimentacao.ENTRADA and lote.validade < date.today():
            raise RegraDeNegocioViolada(
                f"Lote {lote.numero_lote} está vencido ({lote.validade}). "
                "Não é permitido registrar entrada em lote vencido."
            )

        # Não permite dispensação de lote vencido
        if dados.tipo == TipoMovimentacao.DISPENSACAO and lote.validade < date.today():
            raise RegraDeNegocioViolada(
                f"Lote {lote.numero_lote} está vencido ({lote.validade}). "
                "Selecione um lote dentro da validade."
            )