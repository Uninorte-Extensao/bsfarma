"""
Repositório de movimentacao — acesso ao banco de dados.

PADRÃO DO PROJETO — regras do repositório:
  - Só faz queries. Sem lógica de negócio.
  - Recebe AsyncSession via construtor (injetada pelo service).
  - Retorna modelos ORM ou None. Nunca levanta HTTPException.
  - Paginação: sempre com cursor ou limit/offset explícito.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.movimentacao.model import Movimentacao


class MovimentacaoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, movimentacao_id: str) -> Movimentacao | None:
        """Busca uma movimentação pelo UUID. Retorna None se não existir."""
        result = await self.session.execute(
            select(Movimentacao).where(Movimentacao.id == movimentacao_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, lote_id: str | None = None) -> list[Movimentacao]:
        """
        Lista as movimentações ordenadas da mais recente para a mais antiga.

        Args:
            lote_id: Se fornecido, filtra as movimentações de um lote específico.
        """
        # Traz as movimentações mais recentes primeiro (padrão em extratos/estoque)
        stmt = select(Movimentacao).order_by(Movimentacao.ocorrido_em.desc())
        
        if lote_id:
            stmt = stmt.where(Movimentacao.lote_id == lote_id)
            
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, movimentacao: Movimentacao) -> Movimentacao:
        """
        Registra uma nova movimentação no banco.
        """
        self.session.add(movimentacao)
        await self.session.flush()
        await self.session.refresh(movimentacao)
        return movimentacao

    async def update(self, movimentacao: Movimentacao, dados: dict) -> Movimentacao:
        """
        Atualiza campos de uma movimentação existente.
        (Em sistemas de estoque, geralmente atualiza-se apenas a 'justificativa').
        """
        for campo, valor in dados.items():
            setattr(movimentacao, campo, valor)
        await self.session.flush()
        await self.session.refresh(movimentacao)
        return movimentacao