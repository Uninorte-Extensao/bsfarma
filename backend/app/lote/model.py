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
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Lote(Base):
    __tablename__ = "lote"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    
    # Chaves Estrangeiras
    medicamento_id: Mapped[str] = mapped_column(ForeignKey("medicamento.id"), nullable=False)
    registrado_por: Mapped[str] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    
    numero_lote: Mapped[str] = mapped_column(String(100), nullable=False)
    fabricante: Mapped[str] = mapped_column(String(255), nullable=False)
    validade: Mapped[date] = mapped_column(Date, nullable=False)
    
    quantidade_inicial: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_atual: Mapped[int] = mapped_column(Integer, nullable=False)
    
    entrada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Lote id={self.id} numero={self.numero_lote} med_id={self.medicamento_id} qtd_atual={self.quantidade_atual}>"