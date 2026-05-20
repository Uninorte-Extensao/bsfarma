"""
Repositório de dispensacao — acesso ao banco de dados.

PADRÃO DO PROJETO — regras do repositório:
  - Só faz queries. Sem lógica de negócio.
  - Recebe AsyncSession via construtor.
  - Retorna modelos ORM ou None.
  - INTENCIONAL: Sem método update. Dispensações são eventos físicos imutáveis.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dispensacao.model import Dispensacao


class DispensacaoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, dispensacao_id: str) -> Dispensacao | None:
        """Busca uma dispensação pelo UUID. Retorna None se não existir."""
        result = await self.session.execute(
            select(Dispensacao).where(Dispensacao.id == dispensacao_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, paciente_id: str | None = None) -> list[Dispensacao]:
        """
        Lista as dispensações ordenadas da mais recente para a mais antiga.
        Permite filtrar pelo histórico de um paciente específico.
        """
        stmt = select(Dispensacao).order_by(Dispensacao.dispensado_em.desc())
        
        if paciente_id:
            stmt = stmt.where(Dispensacao.paciente_id == paciente_id)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, dispensacao: Dispensacao) -> Dispensacao:
        """Registra o evento de dispensação no banco."""
        self.session.add(dispensacao)
        await self.session.flush()
        await self.session.refresh(dispensacao)
        return dispensacao