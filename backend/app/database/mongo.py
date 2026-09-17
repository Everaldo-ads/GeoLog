import os
from collections.abc import Generator

from pymongo import MongoClient
from pymongo.collection import Collection


mongo_client: MongoClient | None = None
mongo_database = None


def initialize_mongo() -> None:
    global mongo_client, mongo_database
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/geolog")
    mongo_client = MongoClient(mongodb_uri)
    mongo_database = mongo_client.get_default_database()


def get_telemetria_collection() -> Generator[Collection, None, None]:
    if mongo_database is None:
        raise RuntimeError("MongoDB has not been initialized")
    yield mongo_database["telemetrias"]
