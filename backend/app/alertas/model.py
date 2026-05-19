import enum
from typing import TYPE_CHECKING
from datetime import datetime
 
from sqlalchemy import Enum, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
 
from app.db.base import Base
 
if TYPE_CHECKING:
    from app.medicamentos.model import Medicamento
    from app.lote.model import Lote
 
 
class TipoAlerta(str, enum.Enum):
    ALERTA_30_DIAS        = "30 dias para vencimento"
    ALERTA_15_DIAS        = "15 dias para vencimento"
    ALERTA_7_DIAS         = "7 dias para vencimento"
    ALERTA_ESTOQUE_CRITICO = "Estoque Crítico"
 
 
class StatusAlerta(str, enum.Enum):
    PENDENTE     = "Pendente"
    EM_ANDAMENTO = "Em andamento"
    RESOLVIDO    = "Resolvido"
    EXPIRADO     = "Expirado"
 
 
class Alertas(Base):
    __tablename__ = "alertas"
 
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
 
    lote_id: Mapped[str] = mapped_column(
        ForeignKey("lote.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    medicamento_id: Mapped[str] = mapped_column(
        ForeignKey("medicamento.id", ondelete="RESTRICT"), nullable=False, index=True
    )
 
    tipo_alerta: Mapped[TipoAlerta] = mapped_column(
        Enum(TipoAlerta, name="tipo_alerta"), nullable=False
    )
    status_alerta: Mapped[StatusAlerta] = mapped_column(
        Enum(StatusAlerta, name="status_alerta"),
        nullable=False,
        default=StatusAlerta.PENDENTE,
        index=True,
    )
 
    gerado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    resolvido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
 
    # Relacionamentos — back_populates alinhados com Lote e Medicamento
    lote:        Mapped["Lote"]        = relationship(back_populates="alertas")
    medicamento: Mapped["Medicamento"] = relationship(back_populates="alertas")
 
    def __repr__(self) -> str:
        return (
            f"<Alertas id={self.id} "
            f"tipo={self.tipo_alerta.value} "
            f"status={self.status_alerta.value}>"
        )
