from datetime import date

import numpy as np
import pytest

from app.movimentacao.model import TipoMovimentacao
from app.paciente.service import gerar_codigo
from app.previsao.avaliacao import (
    LoteHistorico,
    avaliar_previsao,
    estoque_em,
    historico,
    serie_semanal,
    validar_risco,
)
from app.previsao.risco import LoteEstoque, projetar_perdas, simular_perdas
from app.seed.simulacao import gerar_carga

PROXIMO = LoteEstoque("proximo", validade_dia=13, saldo=30)
DISTANTE = LoteEstoque("distante", validade_dia=100, saldo=50)


def test_projecao_consome_primeiro_o_lote_que_vence_antes():
    assert projetar_perdas([DISTANTE, PROXIMO], 0, consumo_semanal=10) == [0, 10]


def test_simulacao_sem_incerteza_coincide_com_a_projecao():
    riscos = simular_perdas([DISTANTE, PROXIMO], 0, prob_demanda=1.0, tamanhos=np.array([10]), simulacoes=50)
    assert [r.perda_esperada for r in riscos] == [0, 10]
    assert [r.prob_perda for r in riscos] == [0, 1]


def test_simulacao_sem_demanda_perde_todo_o_saldo():
    riscos = simular_perdas([PROXIMO], 0, prob_demanda=0.0, tamanhos=np.array([]), simulacoes=10)
    assert riscos[0].perda_esperada == 30


def test_serie_semanal_agrupa_de_tras_para_frente_e_ignora_fora_da_janela():
    eventos = [(-1, 5), (-7, 3), (-8, 2), (-14, 1), (-15, 9), (0, 100)]
    np.testing.assert_allclose(serie_semanal(eventos, -14, 0), [3, 8])


def test_saldo_em_considera_so_movimentos_anteriores_ao_dia():
    lote = LoteHistorico("l", "L1", -50, 30, 100, [
        (-40, TipoMovimentacao.SAIDA, 10, ""),
        (-10, TipoMovimentacao.SAIDA, 20, ""),
    ])
    assert lote.saldo_em(-40) == 100
    assert lote.saldo_em(-39) == 90
    assert lote.saldo_em(0) == 70


@pytest.fixture(scope="module")
def meds():
    return historico(gerar_carga(date(2026, 10, 30), gerar_codigo))


def test_historico_saidas_batem_com_a_demanda_atendida(meds):
    for med in meds:
        assert sum(q for _, q in med.demanda_real) >= sum(q for _, q in med.saidas)


def test_carga_registra_demanda_nao_atendida_nos_desabastecimentos(meds):
    faltas = {m.nome: sum(q for _, q in m.demanda_real) - sum(q for _, q in m.saidas) for m in meds}
    assert faltas["Losartana Potássica 50 MG"] > 0
    assert sum(1 for f in faltas.values() if f > 0) <= 5


def test_estoque_no_corte_nao_inclui_lotes_que_ainda_nao_chegaram(meds):
    for med in meds:
        for lote in estoque_em(med, -200):
            original = next(l for l in med.lotes if l.id == lote.id)
            assert original.entrada_dia < -200 <= original.validade_dia


def test_avaliacao_cobre_todos_os_medicamentos_com_demanda(meds):
    resultados = [r for m in meds if (r := avaliar_previsao(m))]
    assert len(resultados) >= len(meds) - 1
    assert all(r.mae["Média"] >= 0 for r in resultados)


def test_validacao_de_risco_so_usa_lotes_com_desfecho_conhecido(meds):
    previsoes = validar_risco(meds)
    assert previsoes
    assert all(p.perda_real is not None and p.validade_dia < 0 for p in previsoes)
    assert all(p.corte <= p.validade_dia for p in previsoes)
