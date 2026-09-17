from collections.abc import Sequence

from pymongo.collection import Collection

from ...entities import TelemetriaEntity
from ..interfaces.telemetria import TelemetriaRepository


class MongoTelemetriaRepository(TelemetriaRepository):
    def __init__(self, collection: Collection) -> None:
        self.collection = collection

    def create(self, telemetria: TelemetriaEntity) -> TelemetriaEntity:
        self.collection.insert_one(telemetria.model_dump(mode="json"))
        return telemetria

    def list(self) -> Sequence[TelemetriaEntity]:
        documents = self.collection.find().sort("_id", -1)
        return [TelemetriaEntity.model_validate(document) for document in documents]