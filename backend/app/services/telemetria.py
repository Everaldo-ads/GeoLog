from collections.abc import Sequence

from ..entities import TelemetriaEntity
from ..repository.interfaces.telemetria import TelemetriaRepository
from ..services.geolocation import GeolocationService

from ..types import Location, GeoLocationWebSocketSession

conexoes: dict[str, GeoLocationWebSocketSession] = {}

class TelemetriaService:
    def __init__(self, repository: TelemetriaRepository) -> None:
        self.repository = repository
        self.geolocation_service = GeolocationService()
    
    def create(self, telemetria: TelemetriaEntity) -> TelemetriaEntity:
        return self.repository.create(telemetria)
    
    def list(self) -> Sequence[TelemetriaEntity]:
        return self.repository.list()
    
    def get_last_telemetry(self, veiculo_id: int) -> TelemetriaEntity | None:
        return self.repository.get_last_telemetry(veiculo_id)

    async def distribute_telemetry(self, telemetria: TelemetriaEntity) -> None:
        for _, session in conexoes.items():
            if session.location and session.raio is not None:
                if self.is_nearby(
                    telemetria, 
                    session.location, 
                    session.raio
                ):
                    mensagem = telemetria.model_dump()
                    await session.websocket.send_json(mensagem)

    def is_nearby(self, telemetria: TelemetriaEntity, location: Location, raio: float) -> bool:
        distancia = self.geolocation_service.calculate_distance(
            telemetria.location, location
        )
        return distancia <= raio

    