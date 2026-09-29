from collections.abc import Sequence
from typing import Protocol

from ...entities import TelemetriaEntity


class TelemetriaRepository(Protocol):
    def create(self, telemetria: TelemetriaEntity) -> TelemetriaEntity: ...

    def list(self) -> Sequence[TelemetriaEntity]: ...

    def get_last_telemetry(self, veiculo_id: int) -> TelemetriaEntity | None: ...

    def list_nearby_telemetries(
        self,
        longitude: float,
        latitude: float,
        radius_km: float,
    ) -> Sequence[TelemetriaEntity]: ...

