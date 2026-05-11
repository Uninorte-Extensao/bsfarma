"""
Modelo ORM do medicamento.

PADRÃO DO PROJETO:
  - Herda de Base (app.db.base)
  - Usa UUID como PK gerado pelo banco (server_default)
  - Datas com timezone (TIMESTAMP WITH TIME ZONE no Postgres)
  - Sintaxe SQLAlchemy 2.0 (Mapped / mapped_column)
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.lote.model import Lote
from app.db.base import Base


class Medicamento(Base):
    __tablename__ = "medicamento"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),  # UUID gerado pelo PostgreSQL
    )
    nome_generico: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_comercial: Mapped[str | None] = mapped_column(String(255), nullable=True)
    forma_farmaceutica: Mapped[str] = mapped_column(String(100), nullable=False)
    concentracao: Mapped[str] = mapped_column(String(100), nullable=False)
    via_administracao: Mapped[str] = mapped_column(String(100), nullable=False)

    # Campos opcionais do dataset oficial da ANVISA (coloquei pq achei interessantes, mas não são obrigatórios)
    fabricante: Mapped[str | None]      = mapped_column(String(200), nullable=True)
    cod_ggrem: Mapped[str | None]       = mapped_column(String(30),  nullable=True, unique=True)
    registro_anvisa: Mapped[str | None] = mapped_column(String(30),  nullable=True)
    codigo_barras: Mapped[str | None]   = mapped_column(String(30),  nullable=True)
    classe_terapeutica: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tipo_produto: Mapped[str | None]    = mapped_column(String(30),  nullable=True)
    tarja: Mapped[str | None]           = mapped_column(String(60),  nullable=True)
    restricao_hospitalar: Mapped[bool]  = mapped_column(Boolean, default=False)

    # Campo do programa Farmácia Popular (grupo do remedio, ex: Antidiabético, anticoncepcional, etc)
    indicacao_farmacia_popular: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)

    estoque_minimo: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    atualizado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    lotes: Mapped[list["Lote"]] = relationship(back_populates="medicamento")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Medicamento id={self.id} nome_generico={self.nome_generico} ativo={self.ativo}>"