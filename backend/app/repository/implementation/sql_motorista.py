from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...entities import MotoristaEntity
from ...models import MotoristaModel
from ..interfaces.motorista import MotoristaRepository


class SqlAlchemyMotoristaRepository(MotoristaRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, motorista: MotoristaEntity) -> MotoristaEntity:
        model = MotoristaModel(
            id=str(motorista.id),
            nome=motorista.nome,
            cnh=motorista.cnh,
            status=motorista.status,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return MotoristaEntity.model_validate(model)

    def list(self) -> Sequence[MotoristaEntity]:
        models = self.session.scalars(select(MotoristaModel)).all()
        return [MotoristaEntity.model_validate(model) for model in models]