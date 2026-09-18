from collections.abc import Sequence
from typing import Protocol

from ...entities import VeiculoEntity


class VeiculoRepository(Protocol):
    def create(self, veiculo: VeiculoEntity) -> VeiculoEntity: ...

    def list(self) -> Sequence[VeiculoEntity]: ...
    
    def get_by_id(self, id: str) -> VeiculoEntity | None: ...
    
    def list_by_motorista(self, motorista_id: str) -> Sequence[VeiculoEntity]: ...