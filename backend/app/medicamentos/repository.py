"""
Repositório de medicamento — acesso ao banco de dados.

PADRÃO DO PROJETO — regras do repositório:
  - Só faz queries. Sem lógica de negócio.
  - Recebe AsyncSession via construtor (injetada pelo service).
  - Retorna modelos ORM ou None. Nunca levanta HTTPException.
  - Paginação: sempre com cursor ou limit/offset explícito.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.medicamentos.model import Medicamento


class MedicamentoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, medicamento_id: str) -> Medicamento | None:
        """Busca um medicamento pelo UUID. Retorna None se não existir."""
        result = await self.session.execute(
            select(Medicamento).where(Medicamento.id == medicamento_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, apenas_ativos: bool = True) -> list[Medicamento]:
        """
        Lista todos os medicamentos.

        Args:
            apenas_ativos: Se True (padrão), filtra apenas medicamentos ativos.
        """
        stmt = select(Medicamento)
        if apenas_ativos:
            stmt = stmt.where(Medicamento.ativo == True)  # noqa: E712
        stmt = stmt.order_by(Medicamento.nome_generico)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, medicamento: Medicamento) -> Medicamento:
        """
        Cria um novo medicamento no banco.

        O objeto deve ser criado pelo service antes de chamar este método.
        """
        self.session.add(medicamento)
        await self.session.flush()   # gera o ID sem commitar — o commit é do get_session
        await self.session.refresh(medicamento)
        return medicamento

    async def update(self, medicamento: Medicamento, dados: dict) -> Medicamento:
        """
        Atualiza campos de um medicamento existente.

        Args:
            medicamento: Instância ORM já carregada.
            dados: Dicionário com apenas os campos a atualizar.
        """
        for campo, valor in dados.items():
            setattr(medicamento, campo, valor)
        await self.session.flush()
        await self.session.refresh(medicamento)
        return medicamento

    async def delete(self, medicamento: Medicamento) -> None:
        """
        Remove fisicamente um medicamento do banco.
        """
        await self.session.delete(medicamento)
        await self.session.flush()