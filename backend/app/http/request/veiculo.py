from pydantic import BaseModel, Field


class VeiculoProximoParams(BaseModel):
    latitude: float
    longitude: float
    raio: float
    socket_id: str = Field(min_length=1)


class VeiculoCreateRequest(BaseModel):
    placa: str = Field(min_length=1)
    modelo: str = Field(min_length=1)
    motorista_id: int = Field(gt=0)
