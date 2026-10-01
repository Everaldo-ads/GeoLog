from collections.abc import Sequence

from ..entities import MotoristaEntity
from ..repository.interfaces.motorista import MotoristaRepository


class MotoristaService:
    def __init__(self, repository: MotoristaRepository) -> None:
        self.repository = repository

    def create(self, motorista: MotoristaEntity) -> MotoristaEntity:
        return self.repository.create(motorista)

    def list(self) -> Sequence[MotoristaEntity]:
        return self.repository.list()

    def get_by_id(self, motorista_id: int) -> MotoristaEntity | None:
        return self.repository.get_by_id(motorista_id)