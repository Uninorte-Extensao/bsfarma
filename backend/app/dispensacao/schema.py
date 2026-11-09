"""
Schemas Pydantic do módulo dispensacao.

PADRÃO DO PROJETO:
  - <Entidade>Create  : payload de criação (entrada - atua como DTO para a transação)
  - <Entidade>Response: dados retornados pela API (saída)
  - INTENCIONAL: Sem DispensacaoUpdate. Dispensações não são editáveis.
"""

from datetime import datetime

from pydantic import AliasPath, BaseModel, ConfigDict, Field


class DispensacaoCreate(BaseModel):
    """
    Payload para registrar uma dispensação.
    Note que ele recebe lote_id e quantidade, que NÃO pertencem à tabela dispensacao.
    O Service usará esses dados para criar a Movimentacao vinculada de forma atômica.
    """
    codigo: str = Field(..., description="Código interno do paciente que está recebendo o medicamento")
    lote_id: str = Field(..., description="UUID do lote de onde o medicamento será baixado")
    quantidade: int = Field(..., gt=0, description="Quantidade a ser dispensada", examples=[2])


class DispensacaoResponse(BaseModel):
    """Dados da dispensação retornados pela API."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    paciente_id: str
    movimentacao_id: str
    dispensado_em: datetime


class PacienteResumo(BaseModel):
    """Dados mínimos do paciente embutidos na resposta da dispensação."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    codigo: str


class LoteResumo(BaseModel):
    """Dados mínimos do lote embutidos na resposta da dispensação."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    numero_lote: str


class MedicamentoResumo(BaseModel):
    """Dados mínimos do medicamento embutidos na resposta da dispensação."""
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome_generico: str
    concentracao: str


class DispensacaoDetalhadaResponse(DispensacaoResponse):
    """
    Dispensação com paciente, lote, medicamento e quantidade embutidos,
    para a listagem não precisar buscar movimentações e lotes à parte.
    Quantidade, lote e medicamento vêm da movimentação vinculada.
    """
    paciente: PacienteResumo
    quantidade: int = Field(validation_alias=AliasPath("movimentacao", "quantidade"))
    lote: LoteResumo = Field(validation_alias=AliasPath("movimentacao", "lote"))
    medicamento: MedicamentoResumo = Field(
        validation_alias=AliasPath("movimentacao", "lote", "medicamento")
    )