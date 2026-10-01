from collections.abc import Sequence

from fastapi import HTTPException, status

from ..entities import MotoristaEntity
from ..services.motorista import MotoristaService


class MotoristaController:
    def __init__(self, service: MotoristaService) -> None:
        self.service = service

    def create(self, motorista: MotoristaEntity) -> MotoristaEntity:
        return self.service.create(motorista)

    def list(self) -> Sequence[MotoristaEntity]:
        return self.service.list()

    def get_by_id(self, motorista_id: int) -> MotoristaEntity:
        motorista = self.service.get_by_id(motorista_id)
        if motorista is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Motorista não encontrado",
            )
        return motorista