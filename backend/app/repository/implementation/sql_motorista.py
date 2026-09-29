from collections.abc import Sequence

from sqlalchemy import select

from ...database.sql import create_session
from ...entities import MotoristaEntity
from ...models import MotoristaModel
from ..interfaces.motorista import MotoristaRepository


class SqlAlchemyMotoristaRepository(MotoristaRepository):
    def create(self, motorista: MotoristaEntity) -> MotoristaEntity:
        model = MotoristaModel(
            nome=motorista.nome,
            cnh=motorista.cnh,
            status=motorista.status,
        )
        with create_session() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return MotoristaEntity.model_validate(model)

    def list(self) -> Sequence[MotoristaEntity]:
        with create_session() as session:
            models = session.scalars(select(MotoristaModel)).all()
            return [MotoristaEntity.model_validate(model) for model in models]

    def get_by_id(self, id: int) -> MotoristaEntity | None:
        with create_session() as session:
            model = session.get(MotoristaModel, id)
            return MotoristaEntity.model_validate(model) if model else None