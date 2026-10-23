import asyncio
from datetime import date, datetime, timedelta

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.alertas.scheduler as modulo_scheduler
from app.alertas.model import Alertas, StatusAlerta, TipoAlerta
from app.db.base import Base
from app.lote.model import Lote
from app.main import app as aplicacao
from app.medicamentos.model import Medicamento

JOB_ID = "verificacao_diaria_alertas"


async def _aguardar_parada() -> None:
    for _ in range(100):
        if not modulo_scheduler.scheduler.running:
            return
        await asyncio.sleep(0.01)


async def test_lifespan_inicia_scheduler_com_job_diario_as_00h30_e_encerra():
    async with aplicacao.router.lifespan_context(aplicacao):
        scheduler = modulo_scheduler.scheduler
        job = scheduler.get_job(JOB_ID)

        assert scheduler.running
        assert job is not None
        fuso = scheduler.timezone
        meio_dia = datetime(2026, 10, 23, 12, 0, tzinfo=fuso)
        proximo = job.trigger.get_next_fire_time(None, meio_dia)
        assert proximo == datetime(2026, 10, 24, 0, 30, tzinfo=fuso)
        assert proximo.utcoffset() == timedelta(hours=-4)

    await _aguardar_parada()
    assert not modulo_scheduler.scheduler.running


async def test_job_disparado_pelo_scheduler_gera_alerta_no_banco(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    fabrica = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with fabrica() as sessao:
        medicamento = Medicamento(
            nome_generico="Losartana Potássica",
            forma_farmaceutica="Comprimido",
            concentracao="50 MG",
            via_administracao="Oral",
            estoque_minimo=10,
        )
        sessao.add(medicamento)
        await sessao.flush()
        sessao.add(Lote(
            medicamento_id=medicamento.id,
            numero_lote="SCHED-10D",
            validade=date.today() + timedelta(days=10),
            quantidade_inicial=100,
            quantidade_atual=80,
        ))
        await sessao.commit()

    monkeypatch.setattr(modulo_scheduler, "AsyncSessionLocal", fabrica)
    executado = asyncio.Event()

    def ao_executar(evento):
        if evento.job_id == JOB_ID:
            executado.set()

    try:
        async with aplicacao.router.lifespan_context(aplicacao):
            scheduler = modulo_scheduler.scheduler
            scheduler.add_listener(ao_executar, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
            scheduler.get_job(JOB_ID).modify(next_run_time=datetime.now(scheduler.timezone))
            await asyncio.wait_for(executado.wait(), timeout=10)
            scheduler.remove_listener(ao_executar)
        await _aguardar_parada()

        async with fabrica() as sessao:
            alertas = (await sessao.scalars(select(Alertas))).all()

        assert len(alertas) == 1
        assert alertas[0].tipo_alerta == TipoAlerta.ALERTA_15_DIAS
        assert alertas[0].status_alerta == StatusAlerta.PENDENTE
    finally:
        await engine.dispose()
