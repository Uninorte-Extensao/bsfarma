import math
from dataclasses import dataclass

import numpy as np

DIAS_SEMANA = 7
SIMULACOES_PADRAO = 10_000


@dataclass(frozen=True)
class LoteEstoque:
    id: str
    validade_dia: int
    saldo: int


@dataclass(frozen=True)
class RiscoLote:
    id: str
    saldo: int
    validade_dia: int
    perda_esperada: float
    perda_p90: float
    prob_perda: float


def _semanas_ate(lotes: list[LoteEstoque], inicio: int) -> int:
    ultima = max(l.validade_dia for l in lotes)
    return max(1, math.ceil((ultima - inicio + 1) / DIAS_SEMANA))


def _consumir_fefo(lotes: list[LoteEstoque], inicio: int, demanda: np.ndarray) -> np.ndarray:
    ordem = sorted(range(len(lotes)), key=lambda i: lotes[i].validade_dia)
    saldos = np.tile(np.array([lotes[i].saldo for i in ordem], dtype=float), (demanda.shape[0], 1))
    validades = np.array([lotes[i].validade_dia for i in ordem])
    for semana in range(demanda.shape[1]):
        meio = inicio + semana * DIAS_SEMANA + DIAS_SEMANA // 2
        restante = demanda[:, semana].astype(float)
        for j in np.flatnonzero(validades >= meio):
            retirada = np.minimum(saldos[:, j], restante)
            saldos[:, j] -= retirada
            restante -= retirada
    sobras = np.empty_like(saldos)
    sobras[:, ordem] = saldos
    return sobras


def simular_perdas(
    lotes: list[LoteEstoque],
    inicio: int,
    prob_demanda: float,
    tamanhos: np.ndarray,
    simulacoes: int = SIMULACOES_PADRAO,
    rng: np.random.Generator | None = None,
) -> list[RiscoLote]:
    if not lotes:
        return []
    rng = rng or np.random.default_rng(0)
    semanas = _semanas_ate(lotes, inicio)
    tamanhos = np.asarray(tamanhos, dtype=float)
    if len(tamanhos) == 0 or prob_demanda <= 0:
        demanda = np.zeros((simulacoes, semanas))
    else:
        ocorre = rng.random((simulacoes, semanas)) < min(prob_demanda, 1.0)
        demanda = ocorre * rng.choice(tamanhos, size=(simulacoes, semanas))
    sobras = _consumir_fefo(lotes, inicio, demanda)
    return [
        RiscoLote(
            id=l.id,
            saldo=l.saldo,
            validade_dia=l.validade_dia,
            perda_esperada=float(sobras[:, i].mean()),
            perda_p90=float(np.percentile(sobras[:, i], 90)),
            prob_perda=float((sobras[:, i] > 0).mean()),
        )
        for i, l in enumerate(lotes)
    ]


def projetar_perdas(lotes: list[LoteEstoque], inicio: int, consumo_semanal: float) -> list[float]:
    if not lotes:
        return []
    demanda = np.full((1, _semanas_ate(lotes, inicio)), consumo_semanal)
    return [float(s) for s in _consumir_fefo(lotes, inicio, demanda)[0]]
