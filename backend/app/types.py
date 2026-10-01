from pydantic import BaseModel
from fastapi import WebSocket
from dataclasses import dataclass


class Location(BaseModel):
    latitude: float
    longitude: float


@dataclass
class GeoLocationWebSocketSession:
    raio: float|None
    websocket: WebSocket
    location: Location | None = None
