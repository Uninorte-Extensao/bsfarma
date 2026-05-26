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
import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.dependencies import get_session
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.main import app
from app.usuario.model import PerfilUsuario, Usuario

from dotenv import load_dotenv
from typing import AsyncGenerator

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Add poolclass=NullPool to prevent connection sharing between tests
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    poolclass=NullPool 
)

TestingSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Creates all tables before running tests and drops them after.
    Runs once per test session.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Teardown: Clean up the database after all tests are done
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a new database session for each test.
    Rolls back the transaction after the test completes to ensure a clean slate.
    """
    async with TestingSessionLocal() as session:
        yield session
        # Rollback any uncommitted changes made during the test
        await session.rollback()


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
