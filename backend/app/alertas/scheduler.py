"""
Scheduler de alertas — job diário automático.

Usa APScheduler integrado ao ciclo de vida do FastAPI via lifespan.
O job roda diariamente à 00:30 (horário de Brasília) para garantir
que os alertas do dia estejam disponíveis quando a UBS abrir.

INTEGRAÇÃO COM main.py:
    from contextlib import asynccontextmanager
    from app.alerta.scheduler import iniciar_scheduler, parar_scheduler

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        iniciar_scheduler()
        yield
        parar_scheduler()

    app = FastAPI(lifespan=lifespan)

FUSO HORÁRIO:
    America/Manaus (UTC-4) — sem horário de verão.
    Ajuste para America/Sao_Paulo (UTC-3) se a UBS for em outra região.
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from app.db.session import AsyncSessionLocal
from app.alertas.service import AlertaService

logger = logging.getLogger(__name__)

# Instância única do scheduler — criada no módulo, gerenciada pelo lifespan
scheduler = AsyncIOScheduler(timezone=timezone("America/Manaus"))


async def executar_verificacao() -> None:
    """
    Função executada pelo scheduler.

    Abre uma sessão própria (não usa get_session do FastAPI porque
    não há contexto de requisição HTTP) e chama AlertaService.verificar_todos().
    """
    logger.info("[Scheduler] Iniciando verificação diária de alertas...")
    try:
        async with AsyncSessionLocal() as session:
            service = AlertaService(session)
            resultado = await service.verificar_todos()
            await session.commit()
            logger.info(
                "[Scheduler] Verificação concluída: "
                "criados=%d escalados=%d expirados=%d",
                resultado["alertas_criados"],
                resultado["alertas_escalados"],
                resultado["alertas_expirados"],
            )
    except Exception as e:
        logger.exception("[Scheduler] Erro durante verificação de alertas: ", e)


def iniciar_scheduler() -> None:
    """Registra o job e inicia o scheduler. Chame no lifespan do FastAPI."""
    scheduler.add_job(
        executar_verificacao,
        trigger=CronTrigger(hour=0, minute=30),   # 00:30 horário de Manaus
        id="verificacao_diaria_alertas",
        replace_existing=True,
        misfire_grace_time=3600,    # se o servidor estava offline, executa com até 1h de atraso
    )
    scheduler.start()
    logger.info("[Scheduler] Scheduler de alertas iniciado. Job: 00:30 America/Manaus.")


def parar_scheduler() -> None:
    """Para o scheduler. Chame no lifespan ao encerrar a aplicação."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Scheduler encerrado.")
