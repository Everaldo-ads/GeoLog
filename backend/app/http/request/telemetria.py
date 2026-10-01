from datetime import datetime

from pydantic import BaseModel, Field

from ...types import Location


class TelemetriaCreateRequest(BaseModel):
    location: Location
    temperatura: float
    velocidade: float = Field(ge=0)
    veiculo_id: int = Field(gt=0)
    timestamp: datetime | None = None