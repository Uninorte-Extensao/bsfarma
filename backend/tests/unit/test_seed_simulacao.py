from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

import pytest

from app.movimentacao.model import TipoMovimentacao
from app.paciente.service import gerar_codigo
from app.seed.catalogo import MEDICAMENTOS
from app.seed.simulacao import JANELA_DIAS, gerar_carga
from app.usuario.model import PerfilUsuario

HOJE = date(2026, 10, 23)


@pytest.fixture(scope="module")
def carga():
    return gerar_carga(HOJE, gerar_codigo)


def test_gerar_carga_usuarios_um_por_perfil(carga):
    assert sorted(u["perfil"] for u in carga.usuarios) == sorted(PerfilUsuario)


def test_gerar_carga_medicamentos_carga_inicial_de_cerca_de_25(carga):
    assert len(carga.medicamentos) == len(MEDICAMENTOS)
    assert 20 <= len(carga.medicamentos) <= 30


def test_gerar_carga_saldo_dos_lotes_bate_com_movimentacoes(carga):
    baixas = defaultdict(int)
    for mov in carga.movimentacoes:
        assert mov["tipo"] != TipoMovimentacao.ENTRADA
        baixas[mov["lote_id"]] += mov["quantidade"]
    for lote in carga.lotes:
        assert lote["quantidade_atual"] >= 0
        assert lote["quantidade_atual"] == lote["quantidade_inicial"] - baixas[lote["id"]]


def test_gerar_carga_toda_saida_tem_dispensacao(carga):
    saidas = {m["id"] for m in carga.movimentacoes if m["tipo"] == TipoMovimentacao.SAIDA}
    vinculadas = [d["movimentacao_id"] for d in carga.dispensacoes]
    assert len(vinculadas) == len(set(vinculadas))
    assert set(vinculadas) == saidas


def test_gerar_carga_dispensacoes_cobrem_um_ano_sem_datas_futuras(carga):
    agora = datetime.combine(HOJE, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=5)
    datas = [d["dispensado_em"] for d in carga.dispensacoes]
    assert max(datas) < agora
    assert (agora - min(datas)).days >= JANELA_DIAS - 10


def test_gerar_carga_quantidades_por_dispensacao_variam(carga):
    lote_med = {l["id"]: l["medicamento_id"] for l in carga.lotes}
    quantidades = defaultdict(set)
    for mov in carga.movimentacoes:
        if mov["tipo"] == TipoMovimentacao.SAIDA:
            quantidades[lote_med[mov["lote_id"]]].add(mov["quantidade"])
    variados = sum(1 for qtds in quantidades.values() if len(qtds) > 1)
    assert variados >= len(carga.medicamentos) * 0.8


def test_gerar_carga_codigos_de_paciente_unicos(carga):
    codigos = [p["codigo"] for p in carga.pacientes]
    assert len(codigos) == len(set(codigos))


@pytest.mark.parametrize("deslocamento", range(7))
def test_gerar_carga_qualquer_dia_da_semana_tem_lotes_vencendo_em_30_dias(deslocamento):
    hoje = HOJE + timedelta(days=deslocamento)
    carga = gerar_carga(hoje, gerar_codigo)
    proximos = [
        l for l in carga.lotes
        if l["quantidade_atual"] > 0 and 0 <= (l["validade"] - hoje).days <= 30
    ]
    assert len(proximos) >= 3
    validades = {(l["validade"] - hoje).days for l in carga.lotes if l["quantidade_atual"] > 0}
    assert max(validades) - min(validades) > 365


def test_gerar_carga_mesma_data_e_semente_gera_mesma_carga():
    primeira = gerar_carga(HOJE, gerar_codigo)
    segunda = gerar_carga(HOJE, gerar_codigo)
    assert primeira.lotes == segunda.lotes
    assert primeira.movimentacoes == segunda.movimentacoes
