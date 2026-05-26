"""
Router de usuário — rotas HTTP.

PADRÃO DO PROJETO — regras do router:
  - Instancia o service e delega TUDO a ele. Sem lógica aqui.
  - Declara explicitamente response_model e status_code.
  - Usa Depends() para injetar sessão e usuário autenticado.
  - Segrega acesso por perfil com require_perfil().

Rotas públicas (sem autenticação):
  POST /auth/login

Rotas protegidas:
  POST   /usuarios          → apenas gestor cria usuários
  GET    /usuarios          → gestor e farmacêutico listam
  GET    /usuarios/{id}     → qualquer autenticado
  PATCH  /usuarios/{id}     → apenas gestor
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session, require_perfil
from app.usuario.schema import TokenResponse, UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.usuario.service import UsuarioService

router = APIRouter(tags=["Usuários"])


# ── Autenticação (pública) ───────────────────────────────────────────────────

@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Login — retorna JWT",
)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Autentica com login e senha. Retorna um token JWT Bearer.

    Use o token no header: `Authorization: Bearer <token>`
    """
    service = UsuarioService(session)
    return await service.autenticar(login=form.username, senha=form.password)


# ── CRUD de usuários (protegido) ─────────────────────────────────────────────

@router.post(
    "/usuarios",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuário",
    dependencies=[Depends(require_perfil("gestor"))],
)
async def criar_usuario(
    dados: UsuarioCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = UsuarioService(session)
    return await service.criar(dados)


@router.get(
    "/usuarios",
    response_model=list[UsuarioResponse],
    summary="Listar usuários",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico"))],
)
async def listar_usuarios(
    session: Annotated[AsyncSession, Depends(get_session)],
    apenas_ativos: bool = True,
):
    service = UsuarioService(session)
    return await service.listar(apenas_ativos=apenas_ativos)


@router.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Buscar usuário por ID",
    dependencies=[Depends(require_perfil("gestor", "farmaceutico", "atendente"))],
)
async def buscar_usuario(
    usuario_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = UsuarioService(session)
    return await service.buscar_por_id(usuario_id)


@router.patch(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Atualizar usuário",
    dependencies=[Depends(require_perfil("gestor"))],
)
async def atualizar_usuario(
    usuario_id: str,
    dados: UsuarioUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    service = UsuarioService(session)
    return await service.atualizar(usuario_id, dados)
