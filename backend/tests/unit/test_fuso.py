from datetime import date, datetime, timedelta, timezone

import pytest

import app.core.fuso as fuso
from app.core.exceptions import RegraDeNegocioViolada
from app.lote.model import Lote
from app.movimentacao.model import TipoMovimentacao
from app.movimentacao.schema import MovimentacaoCreate
from app.movimentacao.service import MovimentacaoService
from app.paciente.service import gerar_codigo
from app.seed.simulacao import gerar_carga

NOITE_EM_MANAUS = datetime(2026, 10, 24, 1, 30, tzinfo=timezone.utc)


@pytest.fixture
def relogio(monkeypatch):
    class _Relogio(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOITE_EM_MANAUS.astimezone(tz)

    monkeypatch.setattr(fuso, "datetime", _Relogio)


def test_hoje_ubs_segue_manaus_quando_utc_ja_virou_o_dia(relogio):
    assert NOITE_EM_MANAUS.date() == date(2026, 10, 24)
    assert fuso.hoje_ubs() == date(2026, 10, 23)


def test_limites_do_dia_sao_meia_noite_de_manaus_em_utc():
    dia = date(2026, 10, 23)
    assert fuso.inicio_do_dia(dia) == datetime(2026, 10, 23, 4, 0, tzinfo=timezone.utc)
    assert fuso.fim_do_dia(dia) == datetime(2026, 10, 24, 3, 59, 59, 999999, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("validade", "aceita"),
    [(date(2026, 10, 23), True), (date(2026, 10, 22), False)],
)
async def test_saida_a_noite_respeita_a_validade_no_dia_de_manaus(relogio, validade, aceita):
    lote = Lote(numero_lote="NOITE-01", validade=validade, quantidade_inicial=10, quantidade_atual=10)
    dados = MovimentacaoCreate(lote_id="l", usuario_id="u", tipo=TipoMovimentacao.SAIDA, quantidade=1)
    if aceita:
        await MovimentacaoService._validar(dados, lote)
    else:
        with pytest.raises(RegraDeNegocioViolada):
            await MovimentacaoService._validar(dados, lote)


def test_carga_dispensa_no_expediente_de_manaus():
    carga = gerar_carga(date(2026, 10, 23), gerar_codigo)
    manaus = timezone(timedelta(hours=-4))
    horarios = {d["dispensado_em"].astimezone(manaus).time() for d in carga.dispensacoes}
    assert min(horarios) >= datetime(1, 1, 1, 7, 30).time()
    assert max(horarios) <= datetime(1, 1, 1, 16, 30).time()
