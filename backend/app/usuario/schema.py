"""
Schemas Pydantic do módulo usuario.

PADRÃO DO PROJETO — nomenclatura de schemas:
  - <Entidade>Create  : payload de criação (entrada)
  - <Entidade>Update  : payload de atualização parcial (entrada)
  - <Entidade>Response: dados retornados pela API (saída)

A senha NUNCA aparece no Response — apenas no Create.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.usuario.model import PerfilUsuario


class UsuarioCreate(BaseModel):
    """Payload para criação de um novo usuário."""
    nome: str = Field(min_length=2, max_length=120, examples=["Ana Lima"])
    login: str = Field(min_length=3, max_length=80, examples=["ana.lima"])
    senha: str = Field(min_length=8, description="Mínimo 8 caracteres.")
    perfil: PerfilUsuario = Field(examples=[PerfilUsuario.ATENDENTE])


class UsuarioUpdate(BaseModel):
    """
    Payload para atualização parcial (PATCH).
    Todos os campos são opcionais — envie apenas o que mudar.
    """
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    perfil: PerfilUsuario | None = None
    ativo: bool | None = None


class UsuarioResponse(BaseModel):
    """Dados do usuário retornados pela API. Senha nunca é exposta."""
    model_config = ConfigDict(from_attributes=True)  # permite criar a partir de ORM

    id: str
    nome: str
    login: str
    perfil: PerfilUsuario
    ativo: bool
    criado_em: datetime
    ultimo_acesso: datetime | None


class TokenResponse(BaseModel):
    """Resposta do endpoint de login."""
    access_token: str
    token_type: str = "bearer"
