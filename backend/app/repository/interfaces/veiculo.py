from collections.abc import Sequence
from typing import Protocol

from ...entities import VeiculoEntity


class VeiculoRepository(Protocol):
    def create(self, veiculo: VeiculoEntity) -> VeiculoEntity: ...

    def list(self) -> Sequence[VeiculoEntity]: ...