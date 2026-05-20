"""
Modelo ORM da movimentação.

PADRÃO DO PROJETO:
  - Herda de Base (app.db.base)
  - Usa UUID como PK gerado pelo banco (server_default)
  - Datas com timezone (TIMESTAMP WITH TIME ZONE no Postgres)
  - Sintaxe SQLAlchemy 2.0 (Mapped / mapped_column)
"""

import enum
from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.dispensacao.model import Dispensacao
    from app.lote.model import Lote
    from app.usuario.model import Usuario

class TipoMovimentacao(str, enum.Enum):
    """Tipos possíveis de movimentação de estoque."""
    ENTRADA = "entrada"
    SAIDA = "saida"
    PERDA = "perda"
    AJUSTE = "ajuste"


class Movimentacao(Base):
    __tablename__ = "movimentacao"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    
    # Chaves Estrangeiras (garanta que as tabelas "lote" e "usuario" tenham esses nomes)
    lote_id: Mapped[str] = mapped_column(ForeignKey("lote.id"), nullable=False)
    usuario_id: Mapped[str] = mapped_column(ForeignKey("usuario.id"), nullable=False)
    
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        Enum(TipoMovimentacao, name="tipo_movimentacao"), nullable=False
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    justificativa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    ocorrido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="movimentacoes")  # noqa: F821
    lote: Mapped[List["Lote"]] = relationship(back_populates="movimentacoes")
    dispensacao: Mapped["Dispensacao"] = relationship(back_populates="movimentacao")
    def __repr__(self) -> str:
        return f"<Movimentacao id={self.id} lote={self.lote_id} tipo={self.tipo} qtd={self.quantidade}>"