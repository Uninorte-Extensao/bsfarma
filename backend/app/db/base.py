"""
Base declarativa do SQLAlchemy.

Todos os model.py de domínio devem herdar de Base:
    from app.db.base import Base

    class MeuModelo(Base):
        __tablename__ = "minha_tabela"
        ...
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
