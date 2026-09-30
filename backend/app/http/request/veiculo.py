from pydantic import BaseModel

class VeiculoProximoRequest(BaseModel):
    latitude: float
    longitude: float
    raio: float