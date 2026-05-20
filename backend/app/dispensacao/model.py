"""
Modelo ORM da dispensação.

PADRÃO DO PROJETO:
  - Herda de Base (app.db.base)
  - Usa UUID como PK gerado pelo banco
  - Datas com timezone
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Dispensacao(Base):
    __tablename__ = "dispensacao"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    paciente_id: Mapped[str] = mapped_column(ForeignKey("paciente.id"), nullable=False)
    movimentacao_id: Mapped[str] = mapped_column(ForeignKey("movimentacao.id"), nullable=False)

    dispensado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Dispensacao id={self.id} paciente={self.paciente_id} mov={self.movimentacao_id}>"