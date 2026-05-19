"""
Router de alertas.

Estrutura assimétrica — não há POST de criação nem DELETE:
  - Alertas são criados pelo scheduler ou pela verificação manual.
  - Alertas são imutáveis após RESOLVIDO/EXPIRADO (trilha de auditoria).

Endpoints:
  GET  /alertas                → lista com filtros (painel principal)
  GET  /alertas/{id}           → detalhe completo
  PATCH /alertas/{id}/status   → atendente/farmacêutico atualiza status
  POST /alertas/verificar      → disparo manual (farmacêutico/gestor)
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.alertas.model import StatusAlerta, TipoAlerta
from app.alertas.schema import AlertaResponse, AlertaStatusUpdate, VerificacaoResponse
from app.alertas.service import AlertaService
from app.core.dependencies import get_session, require_perfil

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get(
    "",
    response_model=list[AlertaResponse],
    summary="Listar alertas",
    description=(
        "Retorna alertas com filtros opcionais. Por padrão, lista apenas "
        "alertas ativos (PENDENTE e EM_ANDAMENTO). "
        "Use `apenas_ativos=false` para incluir RESOLVIDO e EXPIRADO."
    ),
    dependencies=[Depends(require_perfil("atendente", "farmaceutico", "gestor"))],
)
async def listar(
    session: Annotated[AsyncSession, Depends(get_session)],
    status_alerta: StatusAlerta | None = Query(
        default=None, alias="status",
        description="Filtra por status específico."
    ),
    tipo: TipoAlerta | None = Query(
        default=None,
        description="Filtra por tipo de alerta."
    ),
    medicamento_id: str | None = Query(
        default=None,
        description="Filtra alertas de um medicamento específico (UUID)."
    ),
    apenas_ativos: bool = Query(
        default=True,
        description="Se true, exclui alertas RESOLVIDO e EXPIRADO."
    ),
):
    return await AlertaService(session).listar(
        status         = status_alerta,
        tipo           = tipo,
        medicamento_id = medicamento_id,
        apenas_ativos  = apenas_ativos,
    )


@router.get(
    "/{alerta_id}",
    response_model=AlertaResponse,
    summary="Detalhe do alerta",
    dependencies=[Depends(require_perfil("atendente", "farmaceutico", "gestor"))],
)
async def buscar_por_id(
    alerta_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await AlertaService(session).buscar_por_id(alerta_id)


@router.patch(
    "/{alerta_id}/status",
    response_model=AlertaResponse,
    summary="Atualizar status do alerta",
    description=(
        "Transições permitidas:\n"
        "- `PENDENTE` → `EM_ANDAMENTO` ou `RESOLVIDO`\n"
        "- `EM_ANDAMENTO` → `RESOLVIDO`\n\n"
        "Alertas `RESOLVIDO` e `EXPIRADO` são estados terminais — "
        "não aceitam novas transições."
    ),
    dependencies=[Depends(require_perfil("atendente", "farmaceutico", "gestor"))],
)
async def atualizar_status(
    alerta_id: str,
    dados: AlertaStatusUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
    usuario=Depends(require_perfil("atendente", "farmaceutico", "gestor")),
):
    return await AlertaService(session).atualizar_status(
        alerta_id  = alerta_id,
        novo_status = dados.status,
        usuario_id  = str(usuario.id),
    )


@router.post(
    "/verificar",
    response_model=VerificacaoResponse,
    status_code=status.HTTP_200_OK,
    summary="Disparar verificação manual de alertas",
    description=(
        "Executa imediatamente a mesma verificação que o scheduler roda à meia-noite. "
        "Útil após receber um novo lote ou após uma perda em massa. "
        "Restrito a farmacêutico e gestor."
    ),
    dependencies=[Depends(require_perfil("farmaceutico", "gestor"))],
)
async def verificar_manualmente(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return await AlertaService(session).verificar_todos()
