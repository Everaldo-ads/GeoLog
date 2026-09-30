from pydantic import BaseModel
from fastapi import WebSocket


class Location(BaseModel):
    latitude: float
    longitude: float


class GeoLocationWebSocketSession(BaseModel):
    websocket: WebSocket
    location: Location | None = None
    raio: float|None
