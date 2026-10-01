from pydantic import BaseModel, Field


class VeiculoProximoRequest(BaseModel):
    latitude: float
    longitude: float
    raio: float


class VeiculoCreateRequest(BaseModel):
    placa: str = Field(min_length=1)
    modelo: str = Field(min_length=1)
    motorista_id: int = Field(gt=0)

class VeiculoProximoRequest(BaseModel):
    latitude: float
    longitude: float
    raio: float