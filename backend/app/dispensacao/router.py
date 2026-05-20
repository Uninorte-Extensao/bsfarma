"""
Router de dispensacao — rotas HTTP.

PADRÃO DO PROJETO:
  - Delega a lógica ao Service.
  - NÃO expõe rota de PATCH ou DELETE (dispensação é um evento físico imutável).
  - Injeta sessão e restringe acessos por perfil.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session, require_perfil
from app.core.dependencies import get_current_user
from app.dispensacao.schema import DispensacaoCreate, DispensacaoResponse
from app.dispensacao.service import DispensacaoService

router = APIRouter(tags=["Dispensações"])


@router.post(
    "/dispensacoes",
    response_model=DispensacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nova dispensação",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def criar_dispensacao(
    dados: DispensacaoCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    # Extrai o usuário da requisição a partir do token criptografado
    usuario_atual = Depends(get_current_user) 
):
    service = DispensacaoService(session)
    # Passa os dados do formulário E a identidade inquestionável do usuário
    return await service.criar(dados, usuario_atual.id)


@router.get(
    "/dispensacoes",
    response_model=list[DispensacaoResponse],
    summary="Listar histórico de dispensações",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def listar_dispensacoes(
    session: Annotated[AsyncSession, Depends(get_session)],
    paciente_id: str | None = None,
):
    service = DispensacaoService(session)
    return await service.listar(paciente_id=paciente_id)


@router.get(
    "/dispensacoes/{dispensacao_id}",
    response_model=DispensacaoResponse,
    summary="Buscar dispensação específica",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def buscar_dispensacao(
    dispensacao_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = DispensacaoService(session)
    return await service.buscar_por_id(dispensacao_id)