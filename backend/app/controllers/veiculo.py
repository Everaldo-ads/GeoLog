from collections.abc import Sequence

from fastapi import HTTPException, status

from ..entities import TelemetriaEntity, VeiculoEntity
from ..http.request.veiculo import VeiculoCreateRequest
from ..repository.interfaces.motorista import MotoristaRepository
from ..services.veiculo import VeiculoService


class VeiculoController:
    def __init__(
        self,
        service: VeiculoService,
        motorista_repository: MotoristaRepository,
    ) -> None:
        self.service = service
        self.motorista_repository = motorista_repository

    def create(self, request: VeiculoCreateRequest) -> VeiculoEntity:
        motorista = self.motorista_repository.get_by_id(request.motorista_id)
        if motorista is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Motorista não encontrado",
            )
        veiculo = VeiculoEntity(
            placa=request.placa,
            modelo=request.modelo,
            motorista=motorista,
        )
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