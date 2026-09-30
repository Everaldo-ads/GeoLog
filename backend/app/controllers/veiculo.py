from collections.abc import Sequence

from fastapi import HTTPException, status

from ..entities import TelemetriaEntity, VeiculoEntity
from ..services.veiculo import VeiculoService


class VeiculoController:
    def __init__(self, service: VeiculoService) -> None:
        self.service = service

    def create(self, veiculo: VeiculoEntity) -> VeiculoEntity:
        return self.service.create(veiculo)

    def list(self) -> Sequence[VeiculoEntity]:
        return self.service.list()

    def list_by_motorista(self, motorista_id: int) -> Sequence[VeiculoEntity]:
        return self.service.list_by_motorista(motorista_id)

    def list_nearby(
        self,
        longitude: float,
        latitude: float,
        radius_km: float,
    ) -> Sequence[TelemetriaEntity]:
        return self.service.list_nearby(
            longitude,
            latitude,
            radius_km,
        )

    def get_by_id(self, veiculo_id: int) -> VeiculoEntity:
        veiculo = self.service.get_by_id(veiculo_id)
        if veiculo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Veículo não encontrado",
            )
        return veiculo