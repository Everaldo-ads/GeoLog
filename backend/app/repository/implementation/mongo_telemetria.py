from collections.abc import Sequence

from pymongo.collection import Collection

from ...entities import TelemetriaEntity
from ..interfaces.telemetria import TelemetriaRepository
from ..interfaces.veiculo import VeiculoRepository


class MongoTelemetriaRepository(TelemetriaRepository):
    def __init__(self, collection: Collection, veiculo_repository: VeiculoRepository) -> None:
        self.collection = collection
        self.veiculo_repository = veiculo_repository

    def create(self, telemetria: TelemetriaEntity) -> TelemetriaEntity:
        doc = telemetria.model_dump(mode="json")
        # remove entity id (Mongo uses its own _id)
        doc.pop("id", None)
        # store only veiculo_id in the collection
        veiculo = doc.pop("veiculo")
        doc["veiculo_id"] = veiculo.get("id")
        self.collection.insert_one(doc)
        return telemetria

    def list(self) -> Sequence[TelemetriaEntity]:
        documents = self.collection.find().sort("_id", -1)
        results: list[TelemetriaEntity] = []
        for document in documents:
            document.pop("_id", None)
            veiculo_id = document.pop("veiculo_id", None)
            if not veiculo_id:
                continue
            veiculo = self.veiculo_repository.get_by_id(veiculo_id)
            if not veiculo:
                continue
            # attach full vehicle data for validation
            document["veiculo"] = veiculo.model_dump(mode="json")
            results.append(TelemetriaEntity.model_validate(document))
        return results