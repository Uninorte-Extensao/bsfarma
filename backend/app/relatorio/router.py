"""
Router de relatórios.

ENDPOINTS DE DADOS (JSON — para dashboards Angular):
  GET /relatorios/dashboard          → resumo geral (alertas + estoque)
  GET /relatorios/consumo-mensal     → consumo agrupado por mês
  GET /relatorios/estoque-atual      → saldo por medicamento
  GET /relatorios/itens-criticos     → lotes que precisam de ação
  GET /relatorios/movimentacoes      → histórico paginado

ENDPOINTS DE EXPORTAÇÃO (arquivo — download direto):
  GET /relatorios/exportar/consumo.csv
  GET /relatorios/exportar/consumo.xlsx
  GET /relatorios/exportar/estoque.xlsx
  GET /relatorios/exportar/movimentacoes.csv

DESIGN PARA O ANGULAR:
  Os endpoints JSON retornam dados prontos para recharts/Chart.js —
  sem processamento no frontend. Os endpoints de exportação retornam
  StreamingResponse com Content-Disposition: attachment, que o navegador
  baixa diretamente ao chamar window.open() ou um <a href> temporário.
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_session, require_perfil
from app.movimentacao.model import TipoMovimentacao
from app.relatorio.schema import (
    ConsumoMensalItem,
    DashboardResumo,
    EstoqueItem,
    FiltroConsumo,
    FiltroMovimentacoes,
    ItemCritico,
    MovimentacoesPaginadas,
)
from app.relatorio.service import RelatorioService

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])

_ACESSO_RELATORIO = [Depends(require_perfil("farmaceutico", "gestor"))]


@router.get(
    "/dashboard",
    response_model=DashboardResumo,
    summary="Resumo geral para o dashboard",
    description=(
        "Retorna em uma única chamada: contagem de alertas abertos por tipo, "
        "métricas de estoque e os 10 itens mais críticos. "
        "Ideal para o widget principal do dashboard Angular."
    ),
    dependencies=_ACESSO_RELATORIO,
)
async def dashboard(session: AsyncSession = Depends(get_session)):
    return await RelatorioService(session).dashboard_resumo()

@router.get(
    "/consumo-mensal",
    response_model=list[ConsumoMensalItem],
    summary="Consumo mensal por medicamento",
    dependencies=_ACESSO_RELATORIO,
)
async def consumo_mensal(
    data_inicio:    date = Query(default_factory=lambda: date.today().replace(day=1) - timedelta(days=180)),
    data_fim:       date = Query(default_factory=date.today),
    medicamento_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    return await RelatorioService(session).consumo_mensal_json(
        data_inicio, data_fim, medicamento_id
    )


@router.get(
    "/estoque-atual",
    response_model=list[EstoqueItem],
    summary="Estoque atual consolidado por medicamento",
    dependencies=_ACESSO_RELATORIO,
)
async def estoque_atual(
    indicacao: str | None = Query(default=None, description="Filtra por indicação do Farmácia Popular"),
    session: AsyncSession = Depends(get_session),
):
    return await RelatorioService(session).estoque_atual_json(indicacao=indicacao)


@router.get(
    "/itens-criticos",
    response_model=list[ItemCritico],
    summary="Lotes que requerem atenção imediata",
    description=(
        "Lista lotes com vencimento nos próximos 30 dias ou "
        "saldo abaixo do estoque mínimo / 10% da quantidade inicial."
    ),
    dependencies=_ACESSO_RELATORIO,
)
async def itens_criticos(session: AsyncSession = Depends(get_session)):
    dados = await RelatorioService(session).repo.itens_criticos()
    return dados


@router.get(
    "/movimentacoes",
    response_model=MovimentacoesPaginadas,
    summary="Histórico de movimentações paginado",
    dependencies=_ACESSO_RELATORIO,
)
async def movimentacoes(
    data_inicio:    date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    data_fim:       date = Query(default_factory=date.today),
    tipo:           TipoMovimentacao | None = Query(default=None),
    medicamento_id: str | None             = Query(default=None),
    page:           int                    = Query(default=1, ge=1),
    page_size:      int                    = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
):
    return await RelatorioService(session).movimentacoes_json(
        data_inicio, data_fim, tipo, medicamento_id, page, page_size
    )


# ── Exportação de arquivos ────────────────────────────────────────────────────

@router.get(
    "/exportar/consumo.csv",
    summary="Exportar consumo mensal como CSV",
    description=(
        "Retorna um arquivo CSV para download. No Angular, dispare com:\n\n"
        "```typescript\n"
        "window.open('/relatorios/exportar/consumo.csv?data_inicio=2025-01-01&data_fim=2025-06-30');\n"
        "```"
    ),
    dependencies=_ACESSO_RELATORIO,
)
async def exportar_consumo_csv(
    data_inicio: date = Query(...),
    data_fim:    date = Query(...),
    session: AsyncSession = Depends(get_session),
):
    conteudo, nome = await RelatorioService(session).exportar_consumo_csv(
        data_inicio, data_fim
    )
    return StreamingResponse(
        iter([conteudo]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@router.get(
    "/exportar/consumo.xlsx",
    summary="Exportar consumo mensal como XLSX",
    dependencies=_ACESSO_RELATORIO,
)
async def exportar_consumo_xlsx(
    data_inicio: date = Query(...),
    data_fim:    date = Query(...),
    session: AsyncSession = Depends(get_session),
):
    conteudo, nome = await RelatorioService(session).exportar_consumo_xlsx(
        data_inicio, data_fim
    )
    return StreamingResponse(
        iter([conteudo]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@router.get(
    "/exportar/estoque.xlsx",
    summary="Exportar estoque atual com abas por indicação",
    dependencies=_ACESSO_RELATORIO,
)
async def exportar_estoque_xlsx(session: AsyncSession = Depends(get_session)):
    conteudo, nome = await RelatorioService(session).exportar_estoque_xlsx()
    return StreamingResponse(
        iter([conteudo]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@router.get(
    "/exportar/movimentacoes.csv",
    summary="Exportar movimentações como CSV",
    dependencies=_ACESSO_RELATORIO,
)
async def exportar_movimentacoes_csv(
    data_inicio: date = Query(...),
    data_fim:    date = Query(...),
    tipo: TipoMovimentacao | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    conteudo, nome = await RelatorioService(session).exportar_movimentacoes_csv(
        data_inicio, data_fim, tipo
    )
    return StreamingResponse(
        iter([conteudo]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )
