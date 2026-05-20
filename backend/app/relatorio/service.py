"""
RelatorioService — formatação de dados e geração de arquivos.

RESPONSABILIDADES:
  - Chama RelatorioRepository para buscar os dados
  - Formata para JSON (dashboards Angular via API)
  - Gera CSV e XLSX (exportação via StreamingResponse)

SEPARAÇÃO DE RESPONSABILIDADES:
  - Repository: SQL e dados brutos
  - Service:    formatação, cálculos derivados, geração de arqivo
  - Router:     HTTP, streaming, headers de download
"""

import io
from datetime import date

import pandas as pd

from sqlalchemy.ext.asyncio import AsyncSession

from app.movimentacao.model import TipoMovimentacao
from app.relatorio.repository import RelatorioRepository


class RelatorioService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = RelatorioRepository(session)

    # ── Dados para dashboards (retornam dict/list para JSON) ─────────────────

    async def dashboard_resumo(self) -> dict:
        """
        Dados consolidados para o widget principal do dashboard Angular.

        Retorna um único objeto com tudo que o dashboard precisa,
        evitando múltiplas chamadas do frontend.
        """
        estoque    = await self.repo.estoque_atual()
        criticos   = await self.repo.itens_criticos()
        alertas    = await self.repo.resumo_alertas()

        # Métricas derivadas
        total_meds    = len(estoque)
        meds_ok       = sum(1 for e in estoque if int(e["saldo_total"]) > int(e["estoque_minimo"]))
        meds_criticos = len(set(c["medicamento_id"] for c in criticos))

        return {
            "alertas":          alertas,
            "estoque": {
                "total_medicamentos":    total_meds,
                "medicamentos_ok":       meds_ok,
                "medicamentos_criticos": meds_criticos,
            },
            "itens_criticos": criticos[:10],   # top 10 mais urgentes para o card
        }

    async def consumo_mensal_json(
        self,
        data_inicio: date,
        data_fim: date,
        medicamento_id: str | None = None,
    ) -> list[dict]:
        """
        Dados de consumo mensal formatados para gráficos (recharts/Chart.js).

        Converte os tipos numéricos do SQLAlchemy para int/float nativos
        para que o JSON seja serializado corretamente pelo FastAPI.
        """
        dados = await self.repo.consumo_mensal(data_inicio, data_fim, medicamento_id)
        return [
            {
                **d,
                "ano":              int(d["ano"]),
                "mes":              int(d["mes"]),
                "total_dispensado": int(d["total_dispensado"]),
                "num_dispensacoes": int(d["num_dispensacoes"]),
                # Label para o eixo X do gráfico: "Jan/2025"
                "periodo": f"{_nome_mes(int(d['mes']))}/{int(d['ano'])}",
            }
            for d in dados
        ]

    async def estoque_atual_json(
        self,
        indicacao: str | None = None,
    ) -> list[dict]:
        dados = await self.repo.estoque_atual(indicacao=indicacao)
        return [
            {
                **d,
                "saldo_total":        int(d["saldo_total"]),
                "num_lotes":          int(d["num_lotes"]),
                "status":             _status_estoque(d),
                "proximo_vencimento": d["proximo_vencimento"].isoformat() if d["proximo_vencimento"] else None,
            }
            for d in dados
        ]

    async def movimentacoes_json(
        self,
        data_inicio: date,
        data_fim: date,
        tipo: TipoMovimentacao | None = None,
        medicamento_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict:
        """
        Histórico paginado de movimentações.

        Retorna envelope com metadados de paginação que o Angular
        usa para montar a tabela e o paginador.
        """
        offset = (page - 1) * page_size
        dados, total = await self.repo.movimentacoes_periodo(
            data_inicio, data_fim, tipo, medicamento_id,
            limit=page_size, offset=offset,
        )
        return {
            "data":        dados,
            "total":       total,
            "page":        page,
            "page_size":   page_size,
            "total_pages": -(-total // page_size),   # ceil division
        }

    # ── Geração de arquivos (retornam bytes para StreamingResponse) ──────────

    async def exportar_consumo_csv(
        self, data_inicio: date, data_fim: date
    ) -> tuple[bytes, str]:
        """
        Gera CSV de consumo mensal.
        Retorna (bytes_do_arquivo, nome_sugerido).
        """
        dados = await self.repo.consumo_mensal(data_inicio, data_fim)
        df    = _consumo_para_dataframe(dados)
        buf   = io.BytesIO()
        df.to_csv(buf, index=False, encoding="utf-8-sig")   # utf-8-sig para Excel no Windows
        nome  = f"consumo_{data_inicio}_{data_fim}.csv"
        return buf.getvalue(), nome

    async def exportar_consumo_xlsx(
        self, data_inicio: date, data_fim: date
    ) -> tuple[bytes, str]:
        """
        Gera XLSX de consumo mensal com formatação básica.
        Retorna (bytes_do_arquivo, nome_sugerido).
        """
        dados = await self.repo.consumo_mensal(data_inicio, data_fim)
        df    = _consumo_para_dataframe(dados)
        buf   = io.BytesIO()

        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Consumo Mensal")

            # Formatação básica — ajusta largura das colunas
            ws = writer.sheets["Consumo Mensal"]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)

        nome = f"consumo_{data_inicio}_{data_fim}.xlsx"
        return buf.getvalue(), nome

    async def exportar_estoque_xlsx(self) -> tuple[bytes, str]:
        """
        Gera XLSX do estoque atual com múltiplas abas por indicação.
        """
        dados = await self.repo.estoque_atual()
        df    = pd.DataFrame(dados)

        # Converte tipos
        df["saldo_total"]  = df["saldo_total"].astype(int)
        df["num_lotes"]    = df["num_lotes"].astype(int)
        df["proximo_vencimento"] = pd.to_datetime(df["proximo_vencimento"]).dt.date

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            # Aba geral
            df.to_excel(writer, index=False, sheet_name="Estoque Geral")

            # Uma aba por indicação do Farmácia Popular
            for indicacao, grupo in df.groupby("indicacao_farmacia_popular"):
                aba = str(indicacao)[:31]   # Excel limita nome de aba a 31 chars
                grupo.to_excel(writer, index=False, sheet_name=aba)

        nome = f"estoque_{date.today().isoformat()}.xlsx"
        return buf.getvalue(), nome

    async def exportar_movimentacoes_csv(
        self,
        data_inicio: date,
        data_fim: date,
        tipo: TipoMovimentacao | None = None,
    ) -> tuple[bytes, str]:
        """
        Exporta todas as movimentações do período (sem paginação).
        """
        dados, _ = await self.repo.movimentacoes_periodo(
            data_inicio, data_fim, tipo, limit=100_000, offset=0
        )
        df  = pd.DataFrame(dados)
        if not df.empty:
            df["ocorrido_em"] = pd.to_datetime(df["ocorrido_em"]).dt.strftime("%d/%m/%Y %H:%M")

        buf  = io.BytesIO()
        df.to_csv(buf, index=False, encoding="utf-8-sig")
        nome = f"movimentacoes_{data_inicio}_{data_fim}.csv"
        return buf.getvalue(), nome


# ── Helpers privados ──────────────────────────────────────────────────────────

def _consumo_para_dataframe(dados: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(dados)
    if df.empty:
        return df
    df["ano"]              = df["ano"].astype(int)
    df["mes"]              = df["mes"].astype(int)
    df["total_dispensado"] = df["total_dispensado"].astype(int)
    df["num_dispensacoes"] = df["num_dispensacoes"].astype(int)
    df["periodo"]          = df.apply(
        lambda r: f"{_nome_mes(r['mes'])}/{r['ano']}", axis=1
    )
    return df[[
        "periodo", "ano", "mes", "nome_generico", "concentracao",
        "total_dispensado", "num_dispensacoes",
    ]]


def _status_estoque(row: dict) -> str:
    saldo    = int(row["saldo_total"])
    minimo   = int(row["estoque_minimo"])
    inicial  = int(row.get("quantidade_inicial") or minimo * 10)
    if saldo == 0:
        return "esgotado"
    if saldo <= minimo or saldo <= inicial * 0.10:
        return "critico"
    if saldo <= minimo * 1.5:
        return "atencao"
    return "ok"


_MESES = ["Jan","Fev","Mar","Abr","Mai","Jun",
          "Jul","Ago","Set","Out","Nov","Dez"]

def _nome_mes(n: int) -> str:
    return _MESES[n - 1] if 1 <= n <= 12 else str(n)
