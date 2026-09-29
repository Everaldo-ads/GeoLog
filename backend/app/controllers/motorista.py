from collections.abc import Sequence

from fastapi import HTTPException, status

from ..entities import MotoristaEntity
from ..repository.interfaces.motorista import MotoristaRepository


class MotoristaController:
    def __init__(self, repository: MotoristaRepository) -> None:
        self.repository = repository

    def create(self, motorista: MotoristaEntity) -> MotoristaEntity:
        return self.repository.create(motorista)

    def list(self) -> Sequence[MotoristaEntity]:
        return self.repository.list()

    def get_by_id(self, motorista_id: int) -> MotoristaEntity:
        motorista = self.repository.get_by_id(motorista_id)
        if motorista is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Motorista não encontrado",
            )
        return motorista