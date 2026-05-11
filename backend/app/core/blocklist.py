# so pra bosta da atv

from datetime import datetime

# { token: datetime_de_expiracao }
_blocklist: dict[str, datetime] = {}


def adicionar(token: str, expira_em: datetime) -> None:
    _purgar_expirados()
    _blocklist[token] = expira_em


def esta_bloqueado(token: str) -> bool:
    _purgar_expirados()
    return token in _blocklist


def _purgar_expirados() -> None:
    agora = datetime.now()
    expirados = [t for t, exp in _blocklist.items() if exp < agora]
    for t in expirados:
        del _blocklist[t]