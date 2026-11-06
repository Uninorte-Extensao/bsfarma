from dataclasses import dataclass

import numpy as np

LIMIAR_ADI = 1.32
LIMIAR_CV2 = 0.49


@dataclass(frozen=True)
class Classificacao:
    eventos: int
    adi: float
    cv2: float
    classe: str


def classificar(serie: np.ndarray) -> Classificacao:
    serie = np.asarray(serie, dtype=float)
    positivos = serie[serie > 0]
    if len(positivos) == 0:
        return Classificacao(0, float("inf"), float("nan"), "sem demanda")
    adi = len(serie) / len(positivos)
    cv2 = float((positivos.std() / positivos.mean()) ** 2)
    if adi < LIMIAR_ADI:
        classe = "suave" if cv2 < LIMIAR_CV2 else "errática"
    else:
        classe = "intermitente" if cv2 < LIMIAR_CV2 else "irregular"
    return Classificacao(len(positivos), adi, cv2, classe)
