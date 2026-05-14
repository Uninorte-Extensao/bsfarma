"""
Service de lote — regras de negócio.

PADRÃO DO PROJETO — regras do service:
  - Orquestra repositórios. Nunca acessa self.session.execute() diretamente.
  - Contém TODA a lógica de negócio (validações, decisões, cálculos).
  - Levanta exceções de domínio ou HTTPException.
  - É a camada testada nos testes unitários (sem banco real).
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNaoEncontrado
from app.lote.model import Lote
from app.lote.repository import LoteRepository
from app.lote.schema import LoteCreate, LoteUpdate


class LoteService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = LoteRepository(session)

    async def criar(self, dados: LoteCreate) -> Lote:
        """
        Registra um novo lote no sistema.
        
        Raises:
            HTTPException 409: Se o lote já existir para o mesmo medicamento.
        """
        existente = await self.repo.get_by_numero_e_medicamento(
            numero_lote=dados.numero_lote, 
            medicamento_id=dados.medicamento_id
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"O lote '{dados.numero_lote}' já está cadastrado para este medicamento.",
            )

        lote = Lote(
            medicamento_id=dados.medicamento_id,
            registrado_por=dados.registrado_por,
            numero_lote=dados.numero_lote,
            fabricante=dados.fabricante,
            validade=dados.validade,
            quantidade_inicial=dados.quantidade_inicial,
            quantidade_atual=dados.quantidade_inicial,  # Regra de negócio: quantidade inicial = atual na criação
        )
        return await self.repo.create(lote)

    async def buscar_por_id(self, lote_id: str) -> Lote:
        """
        Retorna um lote pelo ID.

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
        """
        lote = await self.repo.get_by_id(lote_id)
        if not lote:
            raise RecursoNaoEncontrado("Lote", lote_id)
        return lote

    async def listar(
        self, 
        medicamento_id: str | None = None, 
        apenas_com_saldo: bool = False
    ) -> list[Lote]:
        """
        Lista lotes, permitindo filtros específicos para a operação da farmácia.
        """
        return await self.repo.list_all(
            medicamento_id=medicamento_id, 
            apenas_com_saldo=apenas_com_saldo
        )

    async def atualizar(self, lote_id: str, dados: LoteUpdate) -> Lote:
        """
        Atualiza dados cadastrais de um lote (exceto quantidades).

        Raises:
            RecursoNaoEncontrado: Se o ID não existir.
            HTTPException 409: Se tentar alterar para um número de lote que já existe no mesmo medicamento.
        """
        lote = await self.buscar_por_id(lote_id)
        
        # Validação extra de duplicidade caso o número do lote esteja sendo alterado
        if dados.numero_lote and dados.numero_lote != lote.numero_lote:
            existente = await self.repo.get_by_numero_e_medicamento(
                numero_lote=dados.numero_lote, 
                medicamento_id=lote.medicamento_id
            )
            if existente:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"O lote '{dados.numero_lote}' já existe para este medicamento."
                )

        campos = dados.model_dump(exclude_unset=True)
        return await self.repo.update(lote, campos)