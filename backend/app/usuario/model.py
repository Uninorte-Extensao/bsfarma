"""
Modelo ORM do usuário.

PADRÃO DO PROJETO — siga este modelo em todos os módulos:
  - Herde de Base (app.db.base)
  - Use UUID como PK gerado pelo banco (server_default)
  - Datas com timezone (TIMESTAMP WITH TIME ZONE no Postgres)
  - Enums como strings no banco — mais legível em queries diretas
"""

import enum
from typing import List, TYPE_CHECKING
from datetime import datetime
import app.db.models
from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.movimentacao.model import Movimentacao
    from app.lote.model import Lote

class PerfilUsuario(str, enum.Enum):
    """
    Perfis de acesso do sistema.

    - atendente: registra dispensações no balcão
    - farmaceutico: gerencia estoque, lotes e alertas
    - gestor: acesso total, incluindo relatórios e ajustes
    """
    ATENDENTE = "atendente"
    FARMACEUTICO = "farmaceutico"
    GESTOR = "gestor"


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),  # UUID gerado pelo PostgreSQL
    )
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    login: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(
        Enum(PerfilUsuario, name="perfil_usuario"), nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ultimo_acesso: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    #relacionamentos
    movimentacoes: Mapped[List["Movimentacao"]] = relationship(back_populates="usuario")  # noqa: F821
    lote: Mapped[List["Lote"]] = relationship(back_populates="usuario")

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} login={self.login} perfil={self.perfil}>"