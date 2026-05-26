"""
Fixtures compartilhadas entre todos os testes.

PADRÃO DO PROJETO — fixtures disponíveis:
  - engine_teste     : engine SQLite em memória (rápido, sem Supabase)
  - session          : sessão de banco isolada por teste
  - client           : cliente HTTP do FastAPI (sem servidor real)
  - usuario_gestor   : usuário com perfil gestor já criado no banco
  - token_gestor     : JWT válido do gestor para headers de autenticação
  - usuario_atendente: usuário com perfil atendente
  - token_atendente  : JWT válido do atendente

Para criar fixtures de outros módulos, adicione-as aqui ou crie um
conftest.py dentro da pasta do módulo de teste correspondente.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.dependencies import get_session
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.main import app
from app.usuario.model import PerfilUsuario, Usuario

# Banco SQLite em memória — rápido e isolado, sem depender do Supabase.
DATABASE_URL_TESTE = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine_teste():
    """Engine SQLite em memória. Criada uma vez por sessão de testes."""
    engine = create_async_engine(DATABASE_URL_TESTE, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine_teste):
    """
    Sessão isolada por teste com rollback automático.

    Cada teste começa com banco limpo — sem interferência entre testes.
    """
    factory = async_sessionmaker(bind=engine_teste, class_=AsyncSession, expire_on_commit=False)
    async with factory() as sess:
        yield sess
        await sess.rollback()


@pytest_asyncio.fixture
async def client(session):
    """
    Cliente HTTP assíncrono com banco de teste injetado.

    Substitui get_session pelo session de teste via override de dependência.
    """
    async def get_session_teste():
        yield session

    app.dependency_overrides[get_session] = get_session_teste

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.clear()


# ── Fixtures de usuários ──────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def usuario_gestor(session: AsyncSession) -> Usuario:
    """Usuário com perfil gestor já persistido no banco de teste."""
    usuario = Usuario(
        nome="Gestor Teste",
        login="gestor.teste",
        senha_hash=hash_password("senha-segura-123"),
        perfil=PerfilUsuario.GESTOR,
        ativo=True,
    )
    session.add(usuario)
    await session.flush()
    await session.refresh(usuario)
    return usuario


@pytest_asyncio.fixture
def token_gestor(usuario_gestor: Usuario) -> str:
    """JWT válido para o usuário gestor. Use em headers de requisição."""
    return create_access_token(subject=usuario_gestor.id, perfil=usuario_gestor.perfil)


@pytest_asyncio.fixture
async def usuario_atendente(session: AsyncSession) -> Usuario:
    """Usuário com perfil atendente já persistido no banco de teste."""
    usuario = Usuario(
        nome="Atendente Teste",
        login="atendente.teste",
        senha_hash=hash_password("senha-segura-123"),
        perfil=PerfilUsuario.ATENDENTE,
        ativo=True,
    )
    session.add(usuario)
    await session.flush()
    await session.refresh(usuario)
    return usuario


@pytest_asyncio.fixture
def token_atendente(usuario_atendente: Usuario) -> str:
    """JWT válido para o usuário atendente."""
    return create_access_token(subject=usuario_atendente.id, perfil=usuario_atendente.perfil)
