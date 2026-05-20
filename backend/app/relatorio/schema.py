"""
Schemas Pydantic do módulo relatório.
"""

from datetime import date
from typing import Any
from pydantic import BaseModel, Field, model_validator


class FiltroConsumo(BaseModel):
    """Parâmetros de filtro para relatório de consumo."""
    data_inicio:    date
    data_fim:       date
    medicamento_id: str | None = None

    @model_validator(mode="after")
    def valida_periodo(self):
        if self.data_fim < self.data_inicio:
            raise ValueError("data_fim deve ser maior ou igual a data_inicio.")
        delta = (self.data_fim - self.data_inicio).days
        if delta > 366:
            raise ValueError("O período máximo para exportação é de 366 dias.")
        return self


class FiltroMovimentacoes(BaseModel):
    data_inicio:    date
    data_fim:       date
    tipo:           str | None = None
    medicamento_id: str | None = None
    page:           int        = Field(default=1, ge=1)
    page_size:      int        = Field(default=50, ge=1, le=500)

    @model_validator(mode="after")
    def valida_periodo(self):
        if self.data_fim < self.data_inicio:
            raise ValueError("data_fim deve ser maior ou igual a data_inicio.")
        return self


class ConsumoMensalItem(BaseModel):
    periodo:          str
    ano:              int
    mes:              int
    nome_generico:    str
    concentracao:     str | None
    total_dispensado: int
    num_dispensacoes: int


class ItemCritico(BaseModel):
    lote_id:          str
    numero_lote:      str
    validade:         date
    quantidade_atual: int
    estoque_minimo:   int
    medicamento_id:   str
    nome_generico:    str
    concentracao:     str | None
    motivo:           str


class EstoqueItem(BaseModel):
    medicamento_id:            str
    nome_generico:             str
    concentracao:              str | None
    forma_farmaceutica:        str | None
    via_administracao:         str | None
    indicacao_farmacia_popular: str | None
    estoque_minimo:            int
    saldo_total:               int
    num_lotes:                 int
    proximo_vencimento:        date | None
    status:                    str   # ok | atencao | critico | esgotado


class AlertasResumo(BaseModel):
    dias_30:          int = Field(alias="30_dias")
    dias_15:          int = Field(alias="15_dias")
    dias_7:           int = Field(alias="7_dias")
    estoque_critico:  int
    total:            int

    model_config = {"populate_by_name": True}


class DashboardResumo(BaseModel):
    alertas:          dict[str, Any]
    estoque:          dict[str, int]
    itens_criticos:   list[dict[str, Any]]


class MovimentacoesPaginadas(BaseModel):
    data:        list[dict[str, Any]]
    total:       int
    page:        int
    page_size:   int
    total_pages: int
