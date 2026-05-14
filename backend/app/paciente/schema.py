from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.paciente.model import PerfilPaciente

class PacienteCreate(BaseModel):
    """Payload para criação de um novo paciente."""
    codigo: str = Field(max_length=15)
    condicao_clinica: str = Field(min_length=3, max_length=255)

class PacienteUpdate(BaseModel):
    """
    Payload para atualização de condições clínicas (se aplicável).
    """
    condicao_clinica: str = Field(min_length=3, max_length=255)


class PacienteResponse(BaseModel):
    """Dados do paciente retornados pela API. """
    model_config = ConfigDict(from_attributes=True)  # permite criar a partir de ORM

    codigo: str
    condicao_clinica: str
    ativo: bool
    criado_em: str