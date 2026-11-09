from datetime import date, datetime, time, timezone

from pytz import timezone as fuso_iana

FUSO_UBS = fuso_iana("America/Manaus")


def agora_ubs() -> datetime:
    return datetime.now(FUSO_UBS)


def hoje_ubs() -> date:
    return agora_ubs().date()


def instante_ubs(dia: date, horario: time) -> datetime:
    return FUSO_UBS.localize(datetime.combine(dia, horario)).astimezone(timezone.utc)


def inicio_do_dia(dia: date) -> datetime:
    return instante_ubs(dia, time.min)


def fim_do_dia(dia: date) -> datetime:
    return instante_ubs(dia, time.max)
