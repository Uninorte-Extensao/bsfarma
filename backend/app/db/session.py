"""
Engine assíncrona e fábrica de sessões. Não use AsyncSessionLocal diretamente nas rotas.
Use a dependência get_session() de app.core.dependencies.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=not settings.is_production,  # loga SQL apenas fora de produção
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # evita lazy load após commit em contexto async
)
