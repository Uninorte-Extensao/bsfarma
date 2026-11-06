import numpy as np
import pytest

from app.previsao.classificacao import classificar
from app.previsao.metodos import croston, media, sba, ses, tsb


def test_media_preve_media_acumulada_do_passado():
    np.testing.assert_allclose(media([2, 4, 0]), [np.nan, 2, 3, 2])


def test_ses_atualiza_o_nivel_a_cada_periodo():
    np.testing.assert_allclose(ses([2, 4], alfa=0.5), [np.nan, 2, 3])


def test_croston_so_atualiza_quando_ha_demanda():
    prev = croston([0, 0, 5, 0, 5], alfa=0.5)
    np.testing.assert_allclose(prev, [np.nan, np.nan, np.nan, 5 / 3, 5 / 3, 2])


def test_sba_aplica_correcao_de_vies_sobre_o_croston():
    np.testing.assert_allclose(sba([0, 0, 5, 0, 5], alfa=0.5)[-1], 2 * (1 - 0.5 / 2))


def test_tsb_reduz_a_probabilidade_em_periodos_sem_demanda():
    np.testing.assert_allclose(tsb([0, 4, 0], alfa=0.5, beta=0.5), [np.nan, np.nan, 2, 1])


def test_tsb_tende_a_zero_quando_a_demanda_para_e_croston_nao():
    serie = [10, 0, 10, 0] + [0] * 40
    assert tsb(serie)[-1] < 0.2 * tsb(serie)[4]
    assert croston(serie)[-1] == croston(serie)[4]


@pytest.mark.parametrize(
    ("serie", "classe"),
    [
        ([5, 5, 5, 5], "suave"),
        ([1, 9], "errática"),
        ([10, 0, 0, 10], "intermitente"),
        ([1, 0, 9, 0], "irregular"),
        ([0, 0, 0], "sem demanda"),
    ],
)
def test_classificar_segue_os_limiares_de_syntetos_boylan(serie, classe):
    assert classificar(serie).classe == classe
