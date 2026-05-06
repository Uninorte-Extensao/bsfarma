"""
Service de medicamento — regras de negócio.

PADRÃO DO PROJETO — regras do service:
  - Orquestra repositórios. Nunca acessa self.session.execute() diretamente.
  - Contém TODA a lógica de negócio (validações, decisões, cálculos).
  - Levanta exceções de domínio (app.core.exceptions).
  - É a camada testada nos testes unitários (sem banco real).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado
from app.medicamentos.model import Medicamento
from app.medicamentos.repository import MedicamentoRepository
from app.medicamentos.schema import MedicamentoCreate, MedicamentoUpdate


class MedicamentoService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MedicamentoRepository(session)

    async def criar(self, dados: MedicamentoCreate) -> Medicamento:
        """
        Cria um novo medicamento.
        """
        medicamento = Medicamento(
            nome_generico=dados.nome_generico,
            nome_comercial=dados.nome_comercial,
            forma_farmaceutica=dados.forma_farmaceutica,
            concentracao=dados.concentracao,
            via_administracao=dados.via_administracao,
            estoque_minimo=dados.estoque_minimo,
            ativo=dados.ativo,
        )
        return await self.repo.create(medicamento)

    async def buscar_por_id(self, medicamento_id: str) -> Medicamento:
        """
        Retorna um medicamento pelo ID.

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
        """
        medicamento = await self.repo.get_by_id(medicamento_id)
        if not medicamento:
            raise RecursoNaoEncontrado("Medicamento", medicamento_id)
        return medicamento

    async def listar(self, apenas_ativos: bool = False) -> list[Medicamento]:
        return await self.repo.list_all(apenas_ativos=apenas_ativos)

    async def atualizar(self, medicamento_id: str, dados: MedicamentoUpdate) -> Medicamento:
        """
        Atualiza parcialmente um medicamento.

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
        """
        medicamento = await self.buscar_por_id(medicamento_id)
        # exclude_unset=True garante que só campos enviados sejam atualizados.
        campos = dados.model_dump(exclude_unset=True)
        return await self.repo.update(medicamento, campos)

    async def deletar(self, medicamento_id: str) -> None:
        """
        Remove fisicamente um medicamento.

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
        """
        medicamento = await self.buscar_por_id(medicamento_id)
        await self.repo.delete(medicamento)