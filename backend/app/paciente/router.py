from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session, require_perfil
from app.paciente.schema import PacienteCreate, PacienteResponse, PacienteUpdate, RecuperacaoRequest
from app.paciente.service import PacienteService

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

@router.post(
    "",
    response_model=PacienteResponse,
    summary="Cadastro de Paciente",
    description=(
        "Cadastra um novo paciente a partir do CPF. "
        "O CPF é validado e usado para gerar o código interno pseudonimizado — "
        "não é armazenado no banco. "
        "Se o paciente já estiver cadastrado (mesmo CPF), retorna o cadastro existente."
    ), 
    dependencies=[Depends(require_perfil("atendente", "farmaceutico", "gestor"))],
)

async def criar_paciente(
    dados: PacienteCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PacienteService(session)
    return await service.criar(dados)


@router.get(
    "",
    response_model=list[PacienteResponse],
    summary="Listar pacientes, anonimizados por ID interno.",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def listar_pacientes(
    session: Annotated[AsyncSession, Depends(get_session)],
    apenas_ativos: bool = True,
):
    service = PacienteService(session)
    return await service.listar()


@router.get(
    "/{codigo}",
    response_model=PacienteResponse,
    summary="Buscar paciente por código do cartão",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def buscar_paciente(
    codigo: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PacienteService(session)
    return await service.buscar_por_codigo(codigo)

@router.post(
    "/recuperar",
    response_model=PacienteResponse,
    summary="Recuperar cadastro por CPF (paciente sem cartão)",
    description=(
        "Recupera o cadastro de um paciente que perdeu o cartão com o código interno. "
        "O CPF é verificado presencialmente pelo atendente e usado para recomputar "
        "o código — não é armazenado para entrar em conformidade com a LGPD. "
    ),
    dependencies=[Depends(require_perfil("atendente", "farmaceutico", "gestor"))],
)
async def recuperar_por_cpf(
    dados: RecuperacaoRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await PacienteService(session).recuperar_por_cpf(cpf=dados.cpf)

@router.patch(
    "/{codigo}",
    response_model=PacienteResponse,
    summary="Atualizar condições clínicas do paciente",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def atualizar_paciente(
    codigo: str,
    dados: PacienteUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = PacienteService(session)
    return await service.atualizar(codigo, dados)

@router.delete(
    "/{codigo}/inativar",
    response_model=PacienteResponse,
    summary="Inativar paciente",
    dependencies=[Depends(require_perfil("gestor"))],
)
async def inativar(
    codigo: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await PacienteService(session).inativar(codigo)