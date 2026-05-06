"""
Router de lote — rotas HTTP.

PADRÃO DO PROJETO:
  - Instancia o service e delega TUDO a ele. Sem lógica aqui.
  - Declara explicitamente response_model e status_code.
  - Usa Depends() para injetar sessão.
  - Segrega acesso por perfil com require_perfil().
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session, require_perfil
from app.lote.schema import LoteCreate, LoteResponse, LoteUpdate
from app.lote.service import LoteService

router = APIRouter(tags=["Lotes"])


@router.post(
    "/lotes",
    response_model=LoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar lote",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico"))],
)
async def criar_lote(
    dados: LoteCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = LoteService(session)
    return await service.criar(dados)


@router.get(
    "/lotes",
    response_model=list[LoteResponse],
    summary="Listar lotes",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def listar_lotes(
    session: Annotated[AsyncSession, Depends(get_session)],
    medicamento_id: str | None = None,
    apenas_com_saldo: bool = False,
):
    service = LoteService(session)
    return await service.listar(
        medicamento_id=medicamento_id, 
        apenas_com_saldo=apenas_com_saldo
    )


@router.get(
    "/lotes/{lote_id}",
    response_model=LoteResponse,
    summary="Buscar lote por ID",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def buscar_lote(
    lote_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = LoteService(session)
    return await service.buscar_por_id(lote_id)


@router.patch(
    "/lotes/{lote_id}",
    response_model=LoteResponse,
    summary="Atualizar dados cadastrais do lote",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico"))],
)
async def atualizar_lote(
    lote_id: str,
    dados: LoteUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = LoteService(session)
    return await service.atualizar(lote_id, dados)