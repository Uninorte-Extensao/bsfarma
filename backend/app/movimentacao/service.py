"""
Service de movimentacao — regras de negócio.

PADRÃO DO PROJETO — regras do service:
  - Orquestra repositórios. Nunca acessa self.session.execute() diretamente.
  - Contém TODA a lógica de negócio (validações, decisões, cálculos).
  - Levanta exceções de domínio (app.core.exceptions).
  - É a camada testada nos testes unitários (sem banco real).
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado
from app.movimentacao.model import Movimentacao
from app.movimentacao.repository import MovimentacaoRepository
from app.movimentacao.schema import MovimentacaoCreate, MovimentacaoUpdate


class MovimentacaoService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MovimentacaoRepository(session)

    async def criar(self, dados: MovimentacaoCreate) -> Movimentacao:
        """
        Cria o registro histórico de uma movimentação.
        """
        movimentacao = Movimentacao(
            lote_id=dados.lote_id,
            usuario_id=dados.usuario_id,
            tipo=dados.tipo,
            quantidade=dados.quantidade,
            justificativa=dados.justificativa,
        )
        
        # TODO: Integração futura com o módulo Lote
        # 1. Buscar o lote pelo dados.lote_id
        # 2. Verificar se tipo == SAIDA e se quantidade solicitada > saldo do lote (raise EstoqueInsuficiente)
        # 3. Atualizar o saldo do lote (lote.quantidade -= dados.quantidade)
        # 4. Salvar o lote atualizado
        
        return await self.repo.create(movimentacao)

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