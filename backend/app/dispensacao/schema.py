"""
Schemas Pydantic do módulo dispensacao.

PADRÃO DO PROJETO:
  - <Entidade>Create  : payload de criação (entrada - atua como DTO para a transação)
  - <Entidade>Response: dados retornados pela API (saída)
  - INTENCIONAL: Sem DispensacaoUpdate. Dispensações não são editáveis.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DispensacaoCreate(BaseModel):
    """
    Payload para registrar uma dispensação.
    Note que ele recebe lote_id e quantidade, que NÃO pertencem à tabela dispensacao.
    O Service usará esses dados para criar a Movimentacao vinculada de forma atômica.
    """
    paciente_id: str = Field(..., description="UUID do paciente que está recebendo o medicamento")
    lote_id: str = Field(..., description="UUID do lote de onde o medicamento será baixado")
    quantidade: int = Field(..., gt=0, description="Quantidade a ser dispensada", examples=[2])


class DispensacaoResponse(BaseModel):
    """Dados da dispensação retornados pela API."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    paciente_id: str
    movimentacao_id: str
    dispensado_em: datetime