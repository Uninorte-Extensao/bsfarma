"""
AlertaRepository — queries de banco para o módulo de alertas.

Responsabilidades:
  - Buscar alertas existentes (por lote, por status, por tipo)
  - Verificar duplicatas antes de criar novos alertas
  - Persistir novos alertas e atualizações de status
  - Expirar alertas que perderam relevância

Nenhuma regra de negócio aqui — apenas acesso a dados.
"""

from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.alertas.model import Alertas, StatusAlerta, TipoAlerta


class AlertaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, alerta_id: str) -> Alertas | None:
        result = await self.session.execute(
            select(Alertas)
            .where(Alertas.id == alerta_id)
            .options(
                selectinload(Alertas.lote),
                selectinload(Alertas.medicamento),
            )
        )
        return result.scalar_one_or_none()

    async def listar_ativos(
        self,
        status: list[StatusAlerta] | None = None,
        tipo: TipoAlerta | None = None,
        medicamento_id: str | None = None,
    ) -> list[Alertas]:
        """
        Lista alertas com filtros opcionais.
        Por padrão retorna PENDENTE e EM_ANDAMENTO — os que precisam de ação.
        """
        filtros_ativos = status or [StatusAlerta.PENDENTE, StatusAlerta.EM_ANDAMENTO]

        stmt = (
            select(Alertas)
            .where(Alertas.status.in_(filtros_ativos))
            .options(
                selectinload(Alertas.lote),
                selectinload(Alertas.medicamento),
            )
            .order_by(Alertas.gerado_em.desc())
        )

        if tipo:
            stmt = stmt.where(Alertas.tipo == tipo)
        if medicamento_id:
            stmt = stmt.where(Alertas.medicamento_id == medicamento_id)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def existe_alerta_ativo(
        self,
        lote_id: str,
        tipo: TipoAlerta,
    ) -> bool:
        """
        Verifica se já existe um alerta ativo do mesmo tipo para o lote.
        Evita duplicatas quando o scheduler roda mais de uma vez.
        """
        result = await self.session.execute(
            select(Alertas).where(
                and_(
                    Alertas.lote_id == lote_id,
                    Alertas.tipo    == tipo,
                    Alertas.status.in_([
                        StatusAlerta.PENDENTE,
                        StatusAlerta.EM_ANDAMENTO,
                    ]),
                )
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def criar(self, alerta: Alertas) -> Alertas:
        self.session.add(alerta)
        await self.session.flush()
        await self.session.refresh(alerta)
        return alerta

    async def atualizar_status(
        self,
        alerta: Alertas,
        novo_status: StatusAlerta,
        resolvido_em: datetime | None = None,
    ) -> Alertas:
        alerta.status = novo_status
        if resolvido_em:
            alerta.resolvido_em = resolvido_em
        await self.session.flush()
        await self.session.refresh(alerta)
        return alerta

    async def listar_expirados_candidatos(self) -> list[Alertas]:
        """
        Retorna alertas PENDENTE cujo lote já não representa mais risco:
          - Lote vencido (passou dos 30 dias) e alerta ainda pendente
          - Estoque zerado (perda total registrada)
        A decisão de expirar é do service — o repositório só busca os candidatos.
        """
        result = await self.session.execute(
            select(Alertas)
            .where(Alertas.status == StatusAlerta.PENDENTE)
            .options(selectinload(Alertas.lote))
        )
        return list(result.scalars().all())