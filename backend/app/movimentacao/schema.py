"""
Schemas Pydantic do módulo movimentacao.

PADRÃO DO PROJETO:
  - <Entidade>Create  : payload de criação (entrada)
  - <Entidade>Update  : payload de atualização parcial (entrada)
  - <Entidade>Response: dados retornados pela API (saída)
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.movimentacao.model import TipoMovimentacao


class MovimentacaoCreate(BaseModel):
    """Payload para registro de uma nova movimentação de estoque."""
    lote_id: str = Field(..., description="UUID do lote movimentado")
    usuario_id: str = Field(..., description="UUID do usuário que realizou a operação")
    tipo: TipoMovimentacao = Field(..., examples=[TipoMovimentacao.SAIDA])
    quantidade: int = Field(..., gt=0, description="A quantidade deve ser maior que zero", examples=[10])
    justificativa: str | None = Field(default=None, max_length=255, examples=["Venda no balcão"])


class MovimentacaoUpdate(BaseModel):
    """
    Payload para atualização parcial.
    Em sistemas de controle rigoroso (estoque/farmácia), a quantidade e o tipo
    NÃO devem ser alterados. Se houver erro, estorna-se o lançamento.
    Permitimos apenas a edição da justificativa/observação.
    """
    justificativa: str | None = Field(default=None, max_length=255, examples=["Correção: Retirada para o posto 2"])


class MovimentacaoResponse(BaseModel):
    """Dados da movimentação retornados pela API."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    lote_id: str
    usuario_id: str
    tipo: TipoMovimentacao
    quantidade: int
    justificativa: str | None
    ocorrido_em: datetime