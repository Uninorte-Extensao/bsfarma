"""
Repositório de lote — acesso ao banco de dados.

PADRÃO DO PROJETO — regras do repositório:
  - Só faz queries. Sem lógica de negócio.
  - Recebe AsyncSession via construtor.
  - Retorna modelos ORM ou None. Nunca levanta HTTPException.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.lote.model import Lote


class LoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, lote_id: str) -> Lote | None:
        """Busca um lote pelo UUID. Retorna None se não existir."""
        result = await self.session.execute(
            select(Lote).where(Lote.id == lote_id)
        )
        return result.scalar_one_or_none()

    async def get_by_numero_e_medicamento(self, numero_lote: str, medicamento_id: str) -> Lote | None:
        """
        Busca um lote específico para evitar duplicidade de cadastro 
        do mesmo lote para o mesmo medicamento.
        """
        result = await self.session.execute(
            select(Lote)
            .where(Lote.numero_lote == numero_lote)
            .where(Lote.medicamento_id == medicamento_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self, 
        medicamento_id: str | None = None, 
        apenas_com_saldo: bool = False
    ) -> list[Lote]:
        """
        Lista os lotes, ordenando pela validade (os que vencem primeiro aparecem primeiro).
        """
        stmt = select(Lote).order_by(Lote.validade.asc())
        
        if medicamento_id:
            stmt = stmt.where(Lote.medicamento_id == medicamento_id)
            
        if apenas_com_saldo:
            stmt = stmt.where(Lote.quantidade_atual > 0)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, lote: Lote) -> Lote:
        """Registra um novo lote no banco."""
        self.session.add(lote)
        await self.session.flush()
        await self.session.refresh(lote)
        return lote

    async def update(self, lote: Lote, dados: dict) -> Lote:
        """Atualiza campos de um lote existente."""
        for campo, valor in dados.items():
            setattr(lote, campo, valor)
        await self.session.flush()
        await self.session.refresh(lote)
        return lote