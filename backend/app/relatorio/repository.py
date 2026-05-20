"""
RelatorioRepository — queries analíticas.

Todas as queries pesadas ficam aqui, isoladas da lógica de formatação.
O service decide o que fazer com os dados; o repository só os busca.

QUERIES IMPLEMENTADAS:
  - consumo_mensal:    dispensações agrupadas por mês e medicamento
  - itens_criticos:   lotes com saldo <= mínimo ou validade <= 30 dias
  - estoque_atual:    saldo consolidado por medicamento (soma de lotes)
  - movimentacoes:    histórico filtrado por período, tipo e medicamento
  - alertas_abertos:  contagem por tipo para o dashboard
"""

from datetime import date, datetime
from typing import Any

from sqlalchemy import and_, case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.alertas.model import Alertas, StatusAlerta, TipoAlerta
from app.lote.model import Lote
from app.medicamentos.model import Medicamento
from app.movimentacao.model import Movimentacao, TipoMovimentacao


class RelatorioRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def consumo_mensal(
        self,
        data_inicio: date,
        data_fim: date,
        medicamento_id: str | None = None,
    ) -> list[dict]:
        """
        Dispensações agrupadas por mês e medicamento.

        Retorna:
            [{ ano, mes, medicamento_id, nome_generico, concentracao,
               total_dispensado, num_dispensacoes }]
        """
        stmt = (
            select(
                func.extract("year",  Movimentacao.ocorrido_em).label("ano"),
                func.extract("month", Movimentacao.ocorrido_em).label("mes"),
                Medicamento.id.label("medicamento_id"),
                Medicamento.nome_generico,
                Medicamento.concentracao,
                func.sum(Movimentacao.quantidade).label("total_dispensado"),
                func.count(Movimentacao.id).label("num_dispensacoes"),
            )
            .join(Lote,        Movimentacao.lote_id       == Lote.id)
            .join(Medicamento, Lote.medicamento_id == Medicamento.id)
            .where(
                and_(
                    Movimentacao.tipo == TipoMovimentacao.DISPENSACAO,
                    Movimentacao.ocorrido_em >= datetime.combine(data_inicio, datetime.min.time()),
                    Movimentacao.ocorrido_em <= datetime.combine(data_fim,    datetime.max.time()),
                )
            )
            .group_by(
                func.extract("year",  Movimentacao.ocorrido_em),
                func.extract("month", Movimentacao.ocorrido_em),
                Medicamento.id,
                Medicamento.nome_generico,
                Medicamento.concentracao,
            )
            .order_by("ano", "mes", Medicamento.nome_generico)
        )

        if medicamento_id:
            stmt = stmt.where(Medicamento.id == medicamento_id)

        resultado = await self.session.execute(stmt)
        return [dict(r._mapping) for r in resultado]

    async def itens_criticos(self) -> list[dict]:
        """
        Lotes que exigem atenção imediata:
          - Saldo <= estoque_minimo do medicamento  (limiar absoluto)
          - Saldo <= 10% da quantidade inicial       (limiar relativo)
          - Validade nos próximos 30 dias            (vencimento iminente)

        Retorna:
            [{ lote_id, numero_lote, validade, quantidade_atual,
               quantidade_inicial, estoque_minimo, medicamento_id,
               nome_generico, concentracao, motivo }]
        """
        hoje = date.today()

        stmt = (
            select(
                Lote.id.label("lote_id"),
                Lote.numero_lote,
                Lote.validade,
                Lote.quantidade_atual,
                Lote.quantidade_inicial,
                Lote.fabricante,
                Medicamento.id.label("medicamento_id"),
                Medicamento.nome_generico,
                Medicamento.concentracao,
                Medicamento.estoque_minimo,
                # Coluna calculada: motivo do alerta
                case(
                    (Lote.validade <= hoje + text("INTERVAL '7 days'"),  "Vencimento em 7 dias"),
                    (Lote.validade <= hoje + text("INTERVAL '15 days'"), "Vencimento em 15 dias"),
                    (Lote.validade <= hoje + text("INTERVAL '30 days'"), "Vencimento em 30 dias"),
                    (Lote.quantidade_atual <= Medicamento.estoque_minimo, "Estoque abaixo do mínimo"),
                    else_="Estoque crítico (< 10%)",
                ).label("motivo"),
            )
            .join(Medicamento, Lote.medicamento_id == Medicamento.id)
            .where(
                and_(
                    Lote.quantidade_atual > 0,
                    (
                        (Lote.validade <= hoje + text("INTERVAL '30 days'"))
                        | (Lote.quantidade_atual <= Medicamento.estoque_minimo)
                        | (Lote.quantidade_atual <= Lote.quantidade_inicial * 0.10)
                    ),
                )
            )
            .order_by(Lote.validade.asc(), Lote.quantidade_atual.asc())
        )

        resultado = await self.session.execute(stmt)
        return [dict(r._mapping) for r in resultado]

    async def estoque_atual(
        self,
        apenas_ativos: bool = True,
        indicacao: str | None = None,
    ) -> list[dict]:
        """
        Saldo consolidado por medicamento (soma de todos os lotes com saldo > 0).

        Retorna:
            [{ medicamento_id, nome_generico, concentracao, forma_farmaceutica,
               via_administracao, indicacao_farmacia_popular, estoque_minimo,
               saldo_total, num_lotes, proximo_vencimento }]
        """
        stmt = (
            select(
                Medicamento.id.label("medicamento_id"),
                Medicamento.nome_generico,
                Medicamento.concentracao,
                Medicamento.forma_farmaceutica,
                Medicamento.via_administracao,
                Medicamento.indicacao_farmacia_popular,
                Medicamento.estoque_minimo,
                func.coalesce(func.sum(Lote.quantidade_atual), 0).label("saldo_total"),
                func.count(Lote.id).label("num_lotes"),
                func.min(Lote.validade).label("proximo_vencimento"),
            )
            .outerjoin(
                Lote,
                and_(
                    Lote.medicamento_id == Medicamento.id,
                    Lote.quantidade_atual > 0,
                )
            )
            .group_by(
                Medicamento.id,
                Medicamento.nome_generico,
                Medicamento.concentracao,
                Medicamento.forma_farmaceutica,
                Medicamento.via_administracao,
                Medicamento.indicacao_farmacia_popular,
                Medicamento.estoque_minimo,
            )
            .order_by(Medicamento.nome_generico)
        )

        if apenas_ativos:
            stmt = stmt.where(Medicamento.ativo == True)  # noqa: E712
        if indicacao:
            stmt = stmt.where(Medicamento.indicacao_farmacia_popular == indicacao)

        resultado = await self.session.execute(stmt)
        return [dict(r._mapping) for r in resultado]

    async def movimentacoes_periodo(
        self,
        data_inicio: date,
        data_fim: date,
        tipo: TipoMovimentacao | None = None,
        medicamento_id: str | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        """
        Histórico de movimentações com paginação por offset.
        Retorna (lista, total) para o Angular calcular a paginação.
        """
        base = (
            select(
                Movimentacao.id,
                Movimentacao.tipo,
                Movimentacao.quantidade,
                Movimentacao.justificativa,
                Movimentacao.ocorrido_em,
                Lote.numero_lote,
                Lote.validade,
                Medicamento.id.label("medicamento_id"),
                Medicamento.nome_generico,
                Medicamento.concentracao,
            )
            .join(Lote,        Movimentacao.lote_id       == Lote.id)
            .join(Medicamento, Lote.medicamento_id == Medicamento.id)
            .where(
                and_(
                    Movimentacao.ocorrido_em >= datetime.combine(data_inicio, datetime.min.time()),
                    Movimentacao.ocorrido_em <= datetime.combine(data_fim,    datetime.max.time()),
                )
            )
        )

        if tipo:
            base = base.where(Movimentacao.tipo == tipo)
        if medicamento_id:
            base = base.where(Medicamento.id == medicamento_id)

        # Total para paginação
        total_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(total_stmt)).scalar_one()

        # Dados paginados
        dados_stmt = base.order_by(Movimentacao.ocorrido_em.desc()).limit(limit).offset(offset)
        resultado  = await self.session.execute(dados_stmt)
        dados      = [dict(r._mapping) for r in resultado]

        return dados, total

    async def resumo_alertas(self) -> dict:
        """
        Contagem de alertas abertos por tipo — para o widget do dashboard.

        Retorna:
            { "30_dias": N, "15_dias": N, "7_dias": N, "estoque_critico": N, "total": N }
        """
        stmt = (
            select(
                Alertas.tipo_alerta,
                func.count(Alertas.id).label("total"),
            )
            .where(Alertas.status_alerta.in_([StatusAlerta.PENDENTE, StatusAlerta.EM_ANDAMENTO]))
            .group_by(Alertas.tipo_alerta)
        )
        resultado = await self.session.execute(stmt)
        rows = {r.tipo_alerta: r.total for r in resultado}

        return {
            "30_dias":        rows.get(TipoAlerta.ALERTA_30_DIAS, 0),
            "15_dias":        rows.get(TipoAlerta.ALERTA_15_DIAS, 0),
            "7_dias":         rows.get(TipoAlerta.ALERTA_7_DIAS, 0),
            "estoque_critico": rows.get(TipoAlerta.ALERTA_ESTOQUE_CRITICO, 0),
            "total":          sum(rows.values()),
        }
