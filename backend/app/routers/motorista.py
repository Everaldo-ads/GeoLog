from fastapi import APIRouter, status

from ..controllers.motorista import MotoristaController
from ..entities import MotoristaEntity
from ..repository.implementation.sql_motorista import SqlAlchemyMotoristaRepository
from ..services.motorista import MotoristaService


router = APIRouter(prefix="/api/v1/motoristas", tags=["motoristas"])
motorista_repository = SqlAlchemyMotoristaRepository()
motorista_service = MotoristaService(motorista_repository)
motorista_controller = MotoristaController(motorista_service)


@router.post("", response_model=MotoristaEntity, status_code=status.HTTP_201_CREATED)
def create_motorista(motorista: MotoristaEntity) -> MotoristaEntity:
    return motorista_controller.create(motorista)


@router.get("", response_model=list[MotoristaEntity])
def list_motoristas() -> list[MotoristaEntity]:
    return list(motorista_controller.list())


@router.get("/{motorista_id}", response_model=MotoristaEntity)
def get_motorista(motorista_id: int) -> MotoristaEntity:
    return motorista_controller.get_by_id(motorista_id)