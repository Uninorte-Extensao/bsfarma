"""
Schemas Pydantic do módulo lote.

PADRÃO DO PROJETO:
  - <Entidade>Create  : payload de criação (entrada)
  - <Entidade>Update  : payload de atualização parcial (entrada)
  - <Entidade>Response: dados retornados pela API (saída)
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertasCreate(BaseModel):
    """Payload para registro de um novo lote de medicamento."""
    medicamento_id: str = Field(..., description="UUID do medicamento")
    registrado_por: str = Field(..., description="UUID do usuário que registrou a entrada")
    numero_lote: str = Field(..., min_length=1, max_length=100, examples=["L-202605A"])
    fabricante: str = Field(..., min_length=2, max_length=255, examples=["Medley"])
    validade: date = Field(..., description="Data de validade do lote (YYYY-MM-DD)")
    quantidade_inicial: int = Field(..., gt=0, description="Quantidade de itens que deram entrada", examples=[500])


class AlertasUpdate(BaseModel):
    """
    Payload para atualização parcial.
    As quantidades (inicial e atual) NÃO podem ser alteradas por aqui para 
    manter a integridade do estoque. Use o módulo de movimentação para ajustes de saldo.
    """
    numero_lote: str | None = Field(default=None, min_length=1, max_length=100)
    fabricante: str | None = Field(default=None, min_length=2, max_length=255)
    validade: date | None = None


class AlertasResponse(BaseModel):
    """Dados do lote retornados pela API."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    medicamento_id: str
    registrado_por: str
    numero_lote: str
    fabricante: str
    validade: date
    quantidade_inicial: int
    quantidade_atual: int
    entrada_em: datetime