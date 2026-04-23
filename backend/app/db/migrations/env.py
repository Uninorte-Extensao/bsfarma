"""
Configuração do Alembic para migrações assíncronas.
Para gerar uma nova migration após alterar um model:
    poetry run alembic revision --autogenerate -m "descricao da mudanca"
    poetry run alembic upgrade head

Para reverter a última migration:
    poetry run alembic downgrade -1
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import Base

# Importar TODOS os models aqui para que o Alembic os detecte no autogenerate.
# Adicione uma linha para cada novo módulo criado.
from app.usuario.model import Usuario  # noqa: F401

# Futuros módulos (descomente conforme criar):
# from app.medicamento.model import Medicamento  # noqa: F401
# from app.lote.model import Lote                # noqa: F401
# from app.movimentacao.model import Movimentacao # noqa: F401
# from app.dispensacao.model import Dispensacao   # noqa: F401
# from app.paciente.model import Paciente         # noqa: F401
# from app.alerta.model import Alerta             # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
