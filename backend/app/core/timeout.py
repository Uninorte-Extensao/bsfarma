# pra bosta da atv /2
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class _Tentativas:
    contador: int = 0
    bloqueado_ate: datetime | None = None

_tentativas: dict[str, _Tentativas] = {}

_POLITICA: list[tuple[int, timedelta]] = [
    (5, timedelta(minutes=5)),
    (3, timedelta(seconds=30)),
]


def registrar_falha(login: str) -> None:
    """Incrementa o contador de falhas para o login."""
    estado = _tentativas.setdefault(login, _Tentativas())
    estado.contador += 1

    for minimo, duracao in _POLITICA:
        if estado.contador >= minimo:
            estado.bloqueado_ate = datetime.utcnow() + duracao
            break


def verificar_bloqueio(login: str) -> tuple[bool, int]:
    estado = _tentativas.get(login)
    if not estado or not estado.bloqueado_ate:
        return False, 0

    agora = datetime.now()
    if agora < estado.bloqueado_ate:
        restante = int((estado.bloqueado_ate - agora).total_seconds())
        return True, restante

    resetar(login)
    return False, 0


def resetar(login: str) -> None:
    _tentativas.pop(login, None)