import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class PacienteCreate(BaseModel):
    """
    Payload para criação de um novo paciente. O CPF é usado apenas
    para gerar o código interno, e não é armazenado por questões de privacidade.
    As condições clínicas devem seguir o padrão "condição por extenso (CID-10)",
    como listados nos campos description e examples. Múltiplas condições podem
    listadas e separadas por vírgula.
    """

    cpf: str = Field(
        description="CPF do paciente (com ou sem pontuação).",
        examples=["123.456.789-09", "12345678909"],
    )
    condicao_clinica: str = Field(
        min_length=3, max_length=255,
        description="Condição clínica que justifica o cadastro no programa.",
        examples=["Hipertensão arterial sistêmica (I10)"],
    )
    @field_validator("cpf")
    @classmethod
    def cpf_apenas_digitos_validos(cls, v: str) -> str:
        limpo = re.sub(r'\D', '', v)
        if len(limpo) != 11:
            raise ValueError("CPF deve conter exatamente 11 dígitos.")
        return v  # retorna original — normalização acontece no service
    
class RecuperacaoRequest(BaseModel):
    """
    Payload para recuperação de cadastro por CPF.

    Endpoint separado de PacienteCreate para deixar explícito
    na documentação Swagger que são fluxos distintos.
    """
    cpf: str = Field(
        description="CPF do paciente (com ou sem pontuação).",
        examples=["123.456.789-09", "12345678909"],
    )

    @field_validator("cpf")
    @classmethod
    def cpf_apenas_digitos_validos(cls, v: str) -> str:
        limpo = re.sub(r'\D', '', v)
        if len(limpo) != 11:
            raise ValueError("CPF deve conter exatamente 11 dígitos.")
        return v

class PacienteUpdate(BaseModel):
    """
    Payload para atualização de condições clínicas (se aplicável).
    """
    condicao_clinica: str = Field(min_length=3, max_length=255)


class PacienteResponse(BaseModel):
    """Dados do paciente retornados pela API. """
    model_config = ConfigDict(from_attributes=True)  # permite criar a partir de ORM
    id: str
    codigo: str
    condicao_clinica: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime | None = None