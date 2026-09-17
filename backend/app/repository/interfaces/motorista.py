from collections.abc import Sequence
from typing import Protocol

from ...entities import MotoristaEntity


class MotoristaRepository(Protocol):
    def create(self, motorista: MotoristaEntity) -> MotoristaEntity: ...

    def list(self) -> Sequence[MotoristaEntity]: ...