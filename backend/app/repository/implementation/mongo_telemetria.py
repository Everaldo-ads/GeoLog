from collections.abc import Sequence

from pymongo.collection import Collection

from ...database import mongo
from ...entities import TelemetriaEntity
from ..interfaces.telemetria import TelemetriaRepository
from ..interfaces.veiculo import VeiculoRepository


class MongoTelemetriaRepository(TelemetriaRepository):
    def __init__(self, veiculo_repository: VeiculoRepository) -> None:
        self.veiculo_repository = veiculo_repository

    @staticmethod
    def _get_collection() -> Collection:
        if mongo.mongo_database is None:
            raise RuntimeError("MongoDB has not been initialized")
        return mongo.mongo_database["telemetrias"]

    def create(self, telemetria: TelemetriaEntity) -> TelemetriaEntity:
        doc = telemetria.model_dump(mode="python")
        # remove entity id (Mongo uses its own _id)
        doc.pop("id", None)
        doc["location"] = {
            "type": telemetria.location.type,
            "coordinates": list(telemetria.location.coordinates),
        }
        # store only veiculo_id in the collection
        veiculo = doc.pop("veiculo")
        doc["veiculo_id"] = veiculo.get("id")
        self._get_collection().insert_one(doc)
        return telemetria

    def _to_entity(self, document: dict) -> TelemetriaEntity | None:
        document.pop("_id", None)
        veiculo_id = document.pop("veiculo_id", None)
        if veiculo_id is None:
            return None
        veiculo = self.veiculo_repository.get_by_id(veiculo_id)
        if veiculo is None:
            return None
        document["veiculo"] = veiculo.model_dump(mode="json")
        return TelemetriaEntity.model_validate(document)

    def list(self) -> Sequence[TelemetriaEntity]:
        documents = self._get_collection().find().sort("_id", -1)
        results: list[TelemetriaEntity] = []
        for document in documents:
            telemetria = self._to_entity(document)
            if telemetria is not None:
                results.append(telemetria)
        return results

    def get_last_telemetry(self, veiculo_id: int) -> TelemetriaEntity | None:
        document = self._get_collection().find_one(
            {"veiculo_id": veiculo_id},
            sort=[("timestamp", -1), ("_id", -1)],
        )
        return self._to_entity(document) if document else None

    def list_nearby_telemetries(
        self,
        longitude: float,
        latitude: float,
        radius_km: float,
    ) -> Sequence[TelemetriaEntity]:
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],
                    },
                    "key": "location",
                    "distanceField": "distancia_metros",
                    "spherical": True,
                }
            },
            {"$match": {"veiculo_id": {"$ne": None}}},
            {"$sort": {"veiculo_id": 1, "timestamp": -1, "_id": -1}},
            {
                "$group": {
                    "_id": "$veiculo_id",
                    "ultima_telemetria": {"$first": "$$ROOT"},
                }
            },
            {
                "$match": {
                    "ultima_telemetria.distancia_metros": {
                        "$lte": radius_km * 1000
                    }
                }
            },
            {"$replaceRoot": {"newRoot": "$ultima_telemetria"}},
            {"$sort": {"distancia_metros": 1}},
        ]
        documents = self._get_collection().aggregate(pipeline)
        results: list[TelemetriaEntity] = []
        for document in documents:
            telemetria = self._to_entity(document)
            if telemetria is not None:
                results.append(telemetria)
        return results

