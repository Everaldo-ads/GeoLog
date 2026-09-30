from collections.abc import Sequence

from fastapi import (
    HTTPException, 
    status, 
    BackgroundTasks, 
    WebSocket, 
    WebSocketDisconnect
)

from ..entities import TelemetriaEntity
from ..services.telemetria import TelemetriaService, conexoes

from ..types import GeoLocationWebSocketSession


class TelemetriaController:
    def __init__(self, service: TelemetriaService) -> None:
        self.service = service

    def create(
            self, 
            telemetria: TelemetriaEntity, 
            background_tasks: BackgroundTasks
        ) -> TelemetriaEntity:
        telemetria = self.service.create(telemetria)
        background_tasks.add_task(
            self.service.distribute_telemetry, 
            telemetria
        )
        return telemetria

    def list(self) -> Sequence[TelemetriaEntity]:
        return self.service.list()

    def get_last_telemetry(self, veiculo_id: int) -> TelemetriaEntity | None:
        return self.service.get_last_telemetry(veiculo_id)

    async def connect_websocket(self, websocket: WebSocket) -> None:
        await websocket.accept()
        
        socket_id = websocket.query_params.get("socket_id")
        session = GeoLocationWebSocketSession(
            websocket=websocket,
            location=None,
            raio=None
        )
        conexoes[socket_id] = session
        
        try:
            while True:
                mensagem = await websocket.receive_text()
        except WebSocketDisconnect:
            del conexoes[socket_id]