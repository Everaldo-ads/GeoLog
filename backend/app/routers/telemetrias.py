from fastapi import APIRouter, status

from ..controllers.telemetria import TelemetriaController
from ..entities import TelemetriaEntity
from ..repository.implementation.sql_motorista import SqlAlchemyMotoristaRepository
from ..repository.implementation.sql_veiculo import SqlAlchemyVeiculoRepository
from ..repository.implementation.mongo_telemetria import MongoTelemetriaRepository
from ..repository.interfaces.telemetria import TelemetriaRepository
from ..repository.interfaces.veiculo import VeiculoRepository


router = APIRouter(prefix="/api/v1/telemetrias", tags=["telemetrias"])
motorista_repository = SqlAlchemyMotoristaRepository()
veiculo_repository: VeiculoRepository = SqlAlchemyVeiculoRepository(
    motorista_repository
)
telemetria_repository: TelemetriaRepository = MongoTelemetriaRepository(
    veiculo_repository
)
telemetria_controller = TelemetriaController(telemetria_repository)


@router.post("", response_model=TelemetriaEntity, status_code=status.HTTP_201_CREATED)
def create_telemetria(telemetria: TelemetriaEntity) -> TelemetriaEntity:
    return telemetria_controller.create(telemetria)


@router.get("", response_model=list[TelemetriaEntity])
def list_telemetrias() -> list[TelemetriaEntity]:
    return list(telemetria_controller.list())