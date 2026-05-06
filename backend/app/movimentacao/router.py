"""
Router de movimentacao — rotas HTTP.

PADRÃO DO PROJETO — regras do router:
  - Instancia o service e delega TUDO a ele. Sem lógica aqui.
  - Declara explicitamente response_model e status_code.
  - Usa Depends() para injetar sessão e usuário autenticado.
  - Segrega acesso por perfil com require_perfil().
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session, require_perfil
from app.movimentacao.schema import (
    MovimentacaoCreate,
    MovimentacaoResponse,
    MovimentacaoUpdate
)
from app.movimentacao.service import MovimentacaoService

router = APIRouter(tags=["Movimentações"])


@router.post(
    "/movimentacoes",
    response_model=MovimentacaoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimentação",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def criar_movimentacao(
    dados: MovimentacaoCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = MovimentacaoService(session)
    return await service.criar(dados)


@router.get(
    "/movimentacoes",
    response_model=list[MovimentacaoResponse],
    summary="Listar movimentações",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico"))],
)
async def listar_movimentacoes(
    session: Annotated[AsyncSession, Depends(get_session)],
    lote_id: str | None = None,
):
    service = MovimentacaoService(session)
    return await service.listar(lote_id=lote_id)


@router.get(
    "/movimentacoes/{movimentacao_id}",
    response_model=MovimentacaoResponse,
    summary="Buscar movimentação por ID",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico"))],
)
async def buscar_movimentacao(
    movimentacao_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = MovimentacaoService(session)
    return await service.buscar_por_id(movimentacao_id)


@router.patch(
    "/movimentacoes/{movimentacao_id}",
    response_model=MovimentacaoResponse,
    summary="Atualizar justificativa da movimentação",
    dependencies=[Depends(require_perfil("gestor"))],
)
async def atualizar_movimentacao(
    movimentacao_id: str,
    dados: MovimentacaoUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = MovimentacaoService(session)
    return await service.atualizar(movimentacao_id, dados)