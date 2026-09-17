from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...entities import VeiculoEntity
from ...models import VeiculoModel
from ..interfaces.veiculo import VeiculoRepository


class SqlAlchemyVeiculoRepository(VeiculoRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, veiculo: VeiculoEntity) -> VeiculoEntity:
        model = VeiculoModel(
            id=str(veiculo.id),
            placa=veiculo.placa,
            modelo=veiculo.modelo,
            motorista_id=str(veiculo.motorista_id),
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return VeiculoEntity.model_validate(model)

    def list(self) -> Sequence[VeiculoEntity]:
        models = self.session.scalars(select(VeiculoModel)).all()
        return [VeiculoEntity.model_validate(model) for model in models]