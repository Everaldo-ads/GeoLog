from uuid import UUID, uuid4
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MotoristaEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    nome: str = Field(min_length=1)
    cnh: str = Field(min_length=1)
    status: str = Field(min_length=1)

    model_config = ConfigDict(from_attributes=True)


class VeiculoEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    placa: str = Field(min_length=1)
    modelo: str = Field(min_length=1)
    motorista_id: UUID

    model_config = ConfigDict(from_attributes=True)


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float]


class TelemetriaEntity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    location: GeoJSONPoint
    temperatura: float
    velocidade: float = Field(ge=0)
    veiculo_id: UUID

