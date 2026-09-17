from collections.abc import Sequence
from typing import Protocol

from ...entities import TelemetriaEntity


class TelemetriaRepository(Protocol):
    def create(self, telemetria: TelemetriaEntity) -> TelemetriaEntity: ...

    def list(self) -> Sequence[TelemetriaEntity]: ...