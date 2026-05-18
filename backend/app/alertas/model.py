import enum
from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Enum, ForeignKey, Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.medicamentos.model import Medicamento
    from app.lote.model import Lote

class TipoAlerta(str, enum.Enum):
    """Categorias de alertas divididos em quantidade de dias e estoque mínimo, 
    conforme briefing inicial."""
    ALERTA_30_DIAS = "30 dias para vencimento"
    ALERTA_15_DIAS = "15 dias para vencimento"
    ALERTA_7_DIAS = "7 dias para vencimento"
    ALERTA_ESTOQUE_CRITICO = "Estoque Crítico"

class StatusAlerta(str, enum.Enum):
    """Categorias de status:
        PENDENTE: Alerta gerado pelo sistema que ainda está pendente de ação por um operador.
        EM_ANDAMENTO: Um operador está tratando a ocorrência.
        RESOLVIDO: O problema que gerou o alerta foi corrigido com sucesso.
        EXPIRADO: O tempo limite de relevância do alerta passou sem que houvesse ação.
    """
    PENDENTE = "Pendente"
    EM_ANDAMENTO = "Em andamento"
    RESOLVIDO = "Resolvido"
    EXPIRADO = "Expirado"

class Alertas(Base):
    __tablename__ = "alertas"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),  # UUID gerado pelo PostgreSQL
    )
    lote_id: Mapped[str] = mapped_column(ForeignKey("lote.id"), nullable=False)
    medicamento_id: Mapped[str] = mapped_column(ForeignKey("medicamento.id"), nullable=False)
    tipo_alerta: Mapped[TipoAlerta] = mapped_column(
        Enum(TipoAlerta, name="tipo_alerta"), nullable=False
    )
    status_alerta: Mapped[StatusAlerta] = mapped_column(
        Enum(StatusAlerta, name="status_alerta"), nullable=False
    )
    gerado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolvido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    lote: Mapped["Lote"] = relationship(back_populates="alertas")
    medicamento: Mapped["Medicamento"] = relationship(back_populates="alertas")

    def __repr__(self) -> str:
        return f"<Alertas id={self.id}, tipo_alerta={self.tipo_alerta}, status_alerta={self.status_alerta}"