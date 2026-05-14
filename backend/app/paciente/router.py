from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session, require_perfil
from app.paciente.schema import PacienteCreate, PacienteResponse, PacienteUpdate
from app.paciente.service import PacienteService

router = APIRouter(tags=["Paciente"])

@router.post(
    "/paciente",
    response_model=PacienteResponse,
    summary="Cadastro de Paciente",
)

async def criar_paciente(
    dados: PacienteCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PacienteService(session)
    return await service.criar(dados)


@router.get(
    "/pacientes",
    response_model=list[PacienteResponse],
    summary="Listar pacientes, anonimizados por ID interno.",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def listar_pacientes(
    session: Annotated[AsyncSession, Depends(get_session)],
    apenas_ativos: bool = True,
):
    service = PacienteService(session)
    return await service.listar(apenas_ativos=apenas_ativos)


@router.get(
    "/pacientes/{paciente_id}",
    response_model=PacienteResponse,
    summary="Buscar paciente por ID",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def buscar_paciente(
    paciente_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PacienteService(session)
    return await service.buscar_por_id(paciente_id)

@router.patch(
    "/pacientes/{paciente_id}",
    response_model=PacienteResponse,
    summary="Atualizar condições clínicas do paciente",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def atualizar_paciente(
    paciente_id: str,
    dados: PacienteUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PacienteService(session)
    return await service.atualizar(paciente_id, dados)