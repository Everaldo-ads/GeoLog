from collections.abc import Sequence

from ..entities import TelemetriaEntity, VeiculoEntity
from ..repository.interfaces.telemetria import TelemetriaRepository
from ..repository.interfaces.veiculo import VeiculoRepository


class VeiculoService:
    def __init__(
        self,
        repository: VeiculoRepository,
        telemetria_repository: TelemetriaRepository,
    ) -> None:
        self.repository = repository
        self.telemetria_repository = telemetria_repository

    def create(self, veiculo: VeiculoEntity) -> VeiculoEntity:
        return self.repository.create(veiculo)

    def list(self) -> Sequence[VeiculoEntity]:
        return self.repository.list()

    def list_by_motorista(self, motorista_id: int) -> Sequence[VeiculoEntity]:
        return self.repository.list_by_motorista(motorista_id)

    def list_nearby(
        self,
        longitude: float,
        latitude: float,
        radius_km: float,
    ) -> Sequence[TelemetriaEntity]:
        return self.telemetria_repository.list_nearby_telemetries(
            longitude,
            latitude,
            radius_km,
        )

    def get_by_id(self, veiculo_id: int) -> VeiculoEntity | None:
        return self.repository.get_by_id(veiculo_id)