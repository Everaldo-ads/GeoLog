from collections.abc import Sequence

from ..entities import TelemetriaEntity
from ..repository.interfaces.telemetria import TelemetriaRepository


class TelemetriaController:
    def __init__(self, repository: TelemetriaRepository) -> None:
        self.repository = repository

    def create(self, telemetria: TelemetriaEntity) -> TelemetriaEntity:
        return self.repository.create(telemetria)

    def list(self) -> Sequence[TelemetriaEntity]:
        return self.repository.list()

    def get_last_telemetry(self, veiculo_id: int) -> TelemetriaEntity | None:
        return self.repository.get_last_telemetry(veiculo_id)