import numpy as np

ALFA_PADRAO = 0.1
BETA_PADRAO = 0.05


def _sem_previsao(n: int) -> np.ndarray:
    return np.full(n + 1, np.nan)


def media(serie: np.ndarray) -> np.ndarray:
    serie = np.asarray(serie, dtype=float)
    prev = _sem_previsao(len(serie))
    if len(serie):
        prev[1:] = np.cumsum(serie) / np.arange(1, len(serie) + 1)
    return prev


def ses(serie: np.ndarray, alfa: float = ALFA_PADRAO) -> np.ndarray:
    serie = np.asarray(serie, dtype=float)
    prev = _sem_previsao(len(serie))
    if not len(serie):
        return prev
    nivel = serie[0]
    prev[1] = nivel
    for t in range(1, len(serie)):
        nivel += alfa * (serie[t] - nivel)
        prev[t + 1] = nivel
    return prev


def croston(serie: np.ndarray, alfa: float = ALFA_PADRAO, sba: bool = False) -> np.ndarray:
    serie = np.asarray(serie, dtype=float)
    prev = _sem_previsao(len(serie))
    fator = 1 - alfa / 2 if sba else 1.0
    tamanho = intervalo = None
    desde_ultima = 0
    for t, d in enumerate(serie):
        desde_ultima += 1
        if d > 0:
            if tamanho is None:
                tamanho, intervalo = d, float(desde_ultima)
            else:
                tamanho += alfa * (d - tamanho)
                intervalo += alfa * (desde_ultima - intervalo)
            desde_ultima = 0
        if tamanho is not None:
            prev[t + 1] = fator * tamanho / intervalo
    return prev


def sba(serie: np.ndarray, alfa: float = ALFA_PADRAO) -> np.ndarray:
    return croston(serie, alfa, sba=True)


def tsb(serie: np.ndarray, alfa: float = ALFA_PADRAO, beta: float = BETA_PADRAO) -> np.ndarray:
    serie = np.asarray(serie, dtype=float)
    prev = _sem_previsao(len(serie))
    tamanho = probabilidade = None
    for t, d in enumerate(serie):
        if tamanho is None:
            if d > 0:
                tamanho, probabilidade = d, 1.0 / (t + 1)
        elif d > 0:
            tamanho += alfa * (d - tamanho)
            probabilidade += beta * (1 - probabilidade)
        else:
            probabilidade += beta * (0 - probabilidade)
        if tamanho is not None:
            prev[t + 1] = probabilidade * tamanho
    return prev


METODOS = {
    "Média": media,
    "SES": ses,
    "Croston": croston,
    "SBA": sba,
    "TSB": tsb,
}
