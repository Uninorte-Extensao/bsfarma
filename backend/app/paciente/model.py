from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class Paciente(Base):
    __tablename__ = "paciente"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),  # UUID gerado pelo PostgreSQL
    )
    codigo: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    condicao_clinica: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Paciente id={self.id}, ativo={self.ativo}>"