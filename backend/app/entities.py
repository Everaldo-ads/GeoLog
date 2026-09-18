from typing import Literal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MotoristaEntity(BaseModel):
    id: int | None = Field(default=None)
    nome: str = Field(min_length=1)
    cnh: str = Field(min_length=1)
    status: str = Field(min_length=1)
    
    model_config = ConfigDict(from_attributes=True)


class VeiculoEntity(BaseModel):
    id: int | None = Field(default=None)
    placa: str = Field(min_length=1)
    modelo: str = Field(min_length=1)
    motorista: MotoristaEntity

    model_config = ConfigDict(from_attributes=True)


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float]
    
    model_config = ConfigDict(from_attributes=True)


class TelemetriaEntity(BaseModel):
    id: int | None = Field(default=None)
    location: GeoJSONPoint
    temperatura: float
    velocidade: float = Field(ge=0)
    veiculo: VeiculoEntity
    timestamp: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

