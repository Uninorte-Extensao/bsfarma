"""
Router de medicamentos — rotas HTTP.

PADRÃO DO PROJETO — regras do router:
  - Instancia o service e delega TUDO a ele. Sem lógica aqui.
  - Declara explicitamente response_model e status_code.
  - Usa Depends() para injetar sessão.
  - Segrega acesso por perfil com require_perfil().
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session, require_perfil
from app.medicamentos.schema import (
    MedicamentoCreate,
    MedicamentoResponse,
    MedicamentoUpdate
)
from app.medicamentos.service import MedicamentoService

router = APIRouter(tags=["Medicamentos"])

# ── CRUD de medicamentos (protegido) ─────────────────────────────────────────────

@router.post(
    "/medicamentos",
    response_model=MedicamentoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar medicamento",
    dependencies=[Depends(require_perfil("gestor"))],
)
async def criar_medicamento(
    dados: MedicamentoCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = MedicamentoService(session)
    return await service.criar(dados)


@router.get(
    "/medicamentos",
    response_model=list[MedicamentoResponse],
    summary="Listar medicamentos",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def listar_medicamentos(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = MedicamentoService(session)
    return await service.listar()


@router.get(
    "/medicamentos/{medicamento_id}",
    response_model=MedicamentoResponse,
    summary="Buscar medicamento por ID",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def buscar_medicamento(
    medicamento_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = MedicamentoService(session)
    return await service.buscar_por_id(medicamento_id)


@router.patch(
    "/medicamentos/{medicamento_id}",
    response_model=MedicamentoResponse,
    summary="Atualizar medicamento",
    dependencies=[Depends(require_perfil("gestor"))],
)
async def atualizar_medicamento(
    medicamento_id: str,
    dados: MedicamentoUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = MedicamentoService(session)
    return await service.atualizar(medicamento_id, dados)


@router.delete(
    "/medicamentos/{medicamento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar medicamento",
    dependencies=[Depends(require_perfil("gestor"))],
)
async def deletar_medicamento(
    medicamento_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = MedicamentoService(session)
    await service.deletar(medicamento_id)