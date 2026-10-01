from fastapi import APIRouter, Query, status
from typing import Annotated

from ..controllers.veiculo import VeiculoController
from ..entities import TelemetriaEntity, VeiculoEntity
from ..repository.implementation.sql_motorista import SqlAlchemyMotoristaRepository
from ..repository.implementation.sql_veiculo import SqlAlchemyVeiculoRepository
from ..repository.implementation.mongo_telemetria import MongoTelemetriaRepository
from ..repository.interfaces.telemetria import TelemetriaRepository
from ..repository.interfaces.veiculo import VeiculoRepository
from ..http.request.veiculo import VeiculoCreateRequest, VeiculoProximoParams
from ..services.veiculo import VeiculoService


router = APIRouter(prefix="/api/v1/veiculos", tags=["veiculos"])
motorista_repository = SqlAlchemyMotoristaRepository()
veiculo_repository: VeiculoRepository = SqlAlchemyVeiculoRepository(
    motorista_repository
)
telemetria_repository: TelemetriaRepository = MongoTelemetriaRepository(
    veiculo_repository
)
veiculo_service = VeiculoService(veiculo_repository, telemetria_repository)
veiculo_controller = VeiculoController(
    veiculo_service,
    motorista_repository,
)


@router.post("", response_model=VeiculoEntity, status_code=status.HTTP_201_CREATED)
def create_veiculo(request: VeiculoCreateRequest) -> VeiculoEntity:
    return veiculo_controller.create(request)


@router.get("", response_model=list[VeiculoEntity])
def list_veiculos() -> list[VeiculoEntity]:
    return list(veiculo_controller.list())


@router.get("/motorista/{motorista_id}", response_model=list[VeiculoEntity])
def list_veiculos_by_motorista(motorista_id: int) -> list[VeiculoEntity]:
    return list(veiculo_controller.list_by_motorista(motorista_id))


@router.get("/proximos", response_model=list[TelemetriaEntity])
def list_veiculos_proximos(
    veiculo_proximo: Annotated[VeiculoProximoParams, Query()]
) -> list[TelemetriaEntity]:
    return list(veiculo_controller.list_nearby(veiculo_proximo))


@router.get("/{veiculo_id}", response_model=VeiculoEntity)
def get_veiculo(veiculo_id: int) -> VeiculoEntity:
    return veiculo_controller.get_by_id(veiculo_id)