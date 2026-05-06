"""
Schemas Pydantic do módulo medicamentos.

PADRÃO DO PROJETO — nomenclatura de schemas:
  - <Entidade>Create  : payload de criação (entrada)
  - <Entidade>Update  : payload de atualização parcial (entrada)
  - <Entidade>Response: dados retornados pela API (saída)
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MedicamentoCreate(BaseModel):
    """Payload para criação de um novo medicamento."""
    nome_generico: str = Field(min_length=2, max_length=255, examples=["Dipirona Monoidratada"])
    nome_comercial: str | None = Field(default=None, max_length=255, examples=["Novalgina"])
    forma_farmaceutica: str = Field(min_length=2, max_length=100, examples=["Comprimido"])
    concentracao: str = Field(min_length=1, max_length=100, examples=["500 mg"])
    via_administracao: str = Field(min_length=2, max_length=100, examples=["Oral"])
    estoque_minimo: int = Field(default=0, ge=0, examples=[100])
    ativo: bool = Field(default=True)


class MedicamentoUpdate(BaseModel):
    """
    Payload para atualização parcial (PATCH).
    Todos os campos são opcionais — envie apenas o que mudar.
    """
    nome_generico: str | None = Field(default=None, min_length=2, max_length=255)
    nome_comercial: str | None = Field(default=None, max_length=255)
    forma_farmaceutica: str | None = Field(default=None, min_length=2, max_length=100)
    concentracao: str | None = Field(default=None, min_length=1, max_length=100)
    via_administracao: str | None = Field(default=None, min_length=2, max_length=100)
    estoque_minimo: int | None = Field(default=None, ge=0)
    ativo: bool | None = None


class MedicamentoResponse(BaseModel):
    """Dados do medicamento retornados pela API."""
    model_config = ConfigDict(from_attributes=True)  # permite criar a partir de ORM

    id: str
    nome_generico: str
    nome_comercial: str | None
    forma_farmaceutica: str
    concentracao: str
    via_administracao: str
    estoque_minimo: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime | None