"""
Modelo ORM do lote.

PADRÃO DO PROJETO:
  - Herda de Base (app.db.base)
  - Usa UUID como PK gerado pelo banco (server_default)
  - Datas com timezone (TIMESTAMP WITH TIME ZONE no Postgres) para entrada
  - Data simples (Date) para a validade
  - Sintaxe SQLAlchemy 2.0 (Mapped / mapped_column)
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.medicamentos.model import Medicamento
from app.movimentacao.model import Movimentacao
from app.usuario.model import Usuario

from app.db.base import Base


class Lote(Base):
    __tablename__ = "lote"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    medicamento_id: Mapped[int] = mapped_column(
        ForeignKey("medicamento.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    registrado_por_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuario.id", ondelete="SET NULL"), nullable=True
    )

    numero_lote: Mapped[str]       = mapped_column(String(60), nullable=False)
    fabricante: Mapped[str | None] = mapped_column(String(200), nullable=True)
    validade: Mapped[date]         = mapped_column(Date, nullable=False, index=True)

    quantidade_inicial: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_atual: Mapped[int]   = mapped_column(Integer, nullable=False)

    entrada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos
    medicamento: Mapped["Medicamento"] = relationship(back_populates="lotes")  # noqa: F821
    usuario: Mapped["Usuario"] = relationship(back_populates="lotes")  # noqa: F821
    movimentacoes: Mapped[list["Movimentacao"]] = relationship(back_populates="lote")
    
    def __repr__(self) -> str:
        return f"<Lote id={self.id} numero={self.numero_lote} med_id={self.medicamento_id} qtd_atual={self.quantidade_atual}>"