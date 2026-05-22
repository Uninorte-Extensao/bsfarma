"""
Exceções customizadas e handlers globais.

Registre os handlers em main.py com app.add_exception_handler().
"""

from fastapi import Request
from fastapi.responses import JSONResponse

class ErroInternoServidor(Exception):
    """Levantada em casos de erro interno no servidor."""
    def __init__(self, detalhe: str):
        self.detalhe = detalhe
        super().__init__(detalhe)


class RecursoNaoEncontrado(Exception):
    """Levantada quando um registro não existe no banco."""
    def __init__(self, recurso: str, identificador: str | int):
        self.recurso = recurso
        self.identificador = identificador
        super().__init__(f"{recurso} '{identificador}' não encontrado.")


class EstoqueInsuficiente(Exception):
    """Levantada quando uma movimentação resultaria em estoque negativo."""
    def __init__(self, lote_id: str, disponivel: int, solicitado: int):
        self.lote_id = lote_id
        super().__init__(
            f"Lote {lote_id}: saldo disponível {disponivel}, solicitado {solicitado}."
        )

class RegraDeNegocioViolada(Exception):
    """Levantada para violações gerais de regra de negócio."""
    def __init__(self, detalhe: str):
        self.detalhe = detalhe
        super().__init__(detalhe)

class ErroDeFormulario(Exception):
    """Levantada em casos de mal preenchimento de formulário."""
    def __init__(self, detalhe: str):
        self.detalhe = detalhe
        super().__init__(f"Houve um erro ao processar a requisição: {detalhe}")

# --- Handlers -----------------------------------------------------------

async def handler_erro_servidor(request: Request, exc: ErroInternoServidor):
    return JSONResponse(
        status_code=500,
        content={"detail": exc.detalhe},
    )

async def handler_nao_encontrado(request: Request, exc: RecursoNaoEncontrado):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


async def handler_estoque_insuficiente(request: Request, exc: EstoqueInsuficiente):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


async def handler_regra_violada(request: Request, exc: RegraDeNegocioViolada):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.detalhe},
    )

async def handler_bad_request(request: Request, exc: ErroDeFormulario):
        return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )