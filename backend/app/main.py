"""
Ponto de entrada da aplicação.

Responsabilidades deste arquivo:
  - Criar a instância FastAPI
  - Registrar todos os routers de domínio
  - Registrar handlers de exceção globais
  - Configurar middlewares (CORS etc.)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.exceptions import (
    EstoqueInsuficiente,
    RecursoNaoEncontrado,
    RegraDeNegocioViolada,
    handler_estoque_insuficiente,
    handler_nao_encontrado,
    handler_regra_violada,
)
from app.usuario.router import router as usuario_router
from app.medicamentos.router import router as medicamentos_router
from app.movimentacao.router import router as movimentacao_router
from app.lote.router import router as lote_router
from app.paciente.router import router as paciente_router
from app.dispensacao.router import router as dispensacao_router
from app.alertas.router import router as alertas_router

app = FastAPI(
    title="RemédioEmDia API",
    description="Sistema de controle de estoque da UBS Saúde Sempre.",
    version="0.1.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Em produção, substitua "*" pelos domínios do frontend Angular.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# ── Handlers de exceção ───────────────────────────────────────────────────────
app.add_exception_handler(RecursoNaoEncontrado, handler_nao_encontrado)
app.add_exception_handler(EstoqueInsuficiente, handler_estoque_insuficiente)
app.add_exception_handler(RegraDeNegocioViolada, handler_regra_violada)

# ── Routers ───────────────────────────────────────────────────────────────────
# Adicione um router aqui para cada novo módulo de domínio.
app.include_router(usuario_router)
app.include_router(medicamentos_router)
app.include_router(movimentacao_router)
app.include_router(lote_router)
app.include_router(paciente_router)
app.include_router(alertas_router)
app.include_router(dispensacao_router)
# Exemplo de como registrar os próximos módulos:
# from app.medicamento.router import router as medicamento_router
# app.include_router(medicamento_router, prefix="/medicamentos")
