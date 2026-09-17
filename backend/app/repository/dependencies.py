from typing import Annotated

from fastapi import Depends
from pymongo.collection import Collection
from sqlalchemy.orm import Session

from ..database.mongo import get_telemetria_collection
from ..database.sql import get_sql_session
from .implementation.mongo_telemetria import MongoTelemetriaRepository
from .implementation.sql_motorista import SqlAlchemyMotoristaRepository
from .implementation.sql_veiculo import SqlAlchemyVeiculoRepository


def get_motorista_repository(
    session: Annotated[Session, Depends(get_sql_session)],
) -> SqlAlchemyMotoristaRepository:
    return SqlAlchemyMotoristaRepository(session)


def get_veiculo_repository(
    session: Annotated[Session, Depends(get_sql_session)],
) -> SqlAlchemyVeiculoRepository:
    return SqlAlchemyVeiculoRepository(session)


def get_telemetria_repository(
    collection: Annotated[Collection, Depends(get_telemetria_collection)],
) -> MongoTelemetriaRepository:
    return MongoTelemetriaRepository(collection)
