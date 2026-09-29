from collections.abc import Sequence

from sqlalchemy import select

from ...database.sql import create_session
from ...entities import VeiculoEntity
from ...models import VeiculoModel
from ..interfaces.motorista import MotoristaRepository
from ..interfaces.veiculo import VeiculoRepository


class SqlAlchemyVeiculoRepository(VeiculoRepository):
    def __init__(self, motorista_repository: MotoristaRepository) -> None:
        self.motorista_repository = motorista_repository

    def create(self, veiculo: VeiculoEntity) -> VeiculoEntity:
        model = VeiculoModel(
            placa=veiculo.placa,
            modelo=veiculo.modelo,
            motorista_id=int(veiculo.motorista.id) if veiculo.motorista and veiculo.motorista.id is not None else None,
        )
        with create_session() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
        motorista = self.motorista_repository.get_by_id(model.motorista_id)
        data = {
            "id": model.id,
            "placa": model.placa,
            "modelo": model.modelo,
            "motorista": motorista.model_dump(mode="json") if motorista else None,
        }
        return VeiculoEntity.model_validate(data)

    def list(self) -> Sequence[VeiculoEntity]:
        with create_session() as session:
            models = session.scalars(select(VeiculoModel)).all()
        results: list[VeiculoEntity] = []
        for model in models:
            motorista = self.motorista_repository.get_by_id(model.motorista_id)
            data = {
                "id": model.id,
                "placa": model.placa,
                "modelo": model.modelo,
                "motorista": motorista.model_dump(mode="json") if motorista else None,
            }
            results.append(VeiculoEntity.model_validate(data))
        return results

    def get_by_id(self, id: int) -> VeiculoEntity | None:
        with create_session() as session:
            model = session.get(VeiculoModel, id)
        if not model:
            return None
        motorista = self.motorista_repository.get_by_id(model.motorista_id)
        data = {
            "id": model.id,
            "placa": model.placa,
            "modelo": model.modelo,
            "motorista": motorista.model_dump(mode="json") if motorista else None,
        }
        return VeiculoEntity.model_validate(data)

    def list_by_motorista(self, motorista_id: int) -> Sequence[VeiculoEntity]:
        with create_session() as session:
            models = (
                session.scalars(
                    select(VeiculoModel).where(
                        VeiculoModel.motorista_id == motorista_id
                    )
                )
                .all()
            )
        results: list[VeiculoEntity] = []
        motorista = self.motorista_repository.get_by_id(motorista_id)
        for model in models:
            data = {
                "id": model.id,
                "placa": model.placa,
                "modelo": model.modelo,
                "motorista": motorista.model_dump(mode="json") if motorista else None,
            }
            results.append(VeiculoEntity.model_validate(data))
        return results