from sqlalchemy import ForeignKey, String
from uuid import uuid4
from sqlalchemy.orm import Mapped, mapped_column

from .database.sql import Base


class MotoristaModel(Base):
    __tablename__ = "motoristas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cnh: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)


class VeiculoModel(Base):
    __tablename__ = "veiculos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    placa: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    motorista_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("motoristas.id"), nullable=False
    )
