import os

from pymongo import MongoClient


mongo_client: MongoClient | None = None
mongo_database = None


def initialize_mongo() -> None:
    global mongo_client, mongo_database
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://geolog-mongodb:27017/geolog")
    mongo_client = MongoClient(mongodb_uri)
    mongo_database = mongo_client.get_default_database()
    telemetrias = mongo_database["telemetrias"]
    telemetrias.update_many(
        {"timestamp": {"$type": "string"}},
        [
            {
                "$set": {
                    "timestamp": {
                        "$convert": {
                            "input": "$timestamp",
                            "to": "date",
                            "onError": None,
                            "onNull": None,
                        }
                    }
                }
            }
        ],
    )
    telemetrias.create_index(
        [("location", "2dsphere")],
        name="location_2dsphere",
    )
    telemetrias.create_index(
        [("veiculo_id", 1), ("timestamp", -1)],
        name="veiculo_timestamp_desc",
    )
