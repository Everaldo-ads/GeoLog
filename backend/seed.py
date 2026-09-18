import os
import time
from pathlib import Path

from pymongo.errors import PyMongoError

from app.database.sql import initialize_sql, SessionLocal, Base
from app.database.mongo import initialize_mongo, mongo_database
from app.models import MotoristaModel, VeiculoModel

# try to load .env if present
env_path = Path(__file__).with_name(".env")
if env_path.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
    except Exception:
        # dotenv not installed, skip
        pass

MOTORISTAS = [
    (1, "Carlos Andrade", "123456789", "Ativo"),
    (2, "Mariana Silva", "987654321", "Ativo"),
    (3, "Roberto Souza", "456789123", "Em Descanso"),
]
VEICULOS = [
    (101, "ABC-1A23", "Volvo FH 540", 1),
    (102, "XYZ-9876", "Scania R450", 2),
    (103, "KGB-4567", "Mercedes Actros", 3),
]
TELEMETRIA_SEED = [
    {
        "veiculo_id": 101,
        "location": {"type": "Point", "coordinates": [-34.873, -7.115]},
        "temperatura": 4.2,
        "velocidade": 65,
        "timestamp": "2026-09-11T10:00:00Z",
    },
    {
        "veiculo_id": 102,
        "location": {"type": "Point", "coordinates": [-34.832, -7.121]},
        "temperatura": -18.5,
        "velocidade": 85,
        "timestamp": "2026-09-11T10:05:00Z",
    },
    {
        "veiculo_id": 103,
        "location": {"type": "Point", "coordinates": [-34.95, -7.15]},
        "temperatura": 22.0,
        "velocidade": 0,
        "timestamp": "2026-09-11T09:45:00Z",
    },
]


def seed_sql():
    engine = initialize_sql()
    # create tables
    Base.metadata.create_all(engine)

    Session = SessionLocal
    if Session is None:
        raise RuntimeError("SessionLocal not initialized")

    session = Session()
    try:
        # clear existing
        session.query(MotoristaModel).delete()
        session.query(VeiculoModel).delete()
        session.commit()

        # insert motoristas
        for mid, nome, cnh, status in MOTORISTAS:
            m = MotoristaModel(id=mid, nome=nome, cnh=cnh, status=status)
            session.add(m)

        # insert veiculos
        for vid, placa, modelo, motorista_id in VEICULOS:
            v = VeiculoModel(id=vid, placa=placa, modelo=modelo, motorista_id=motorista_id)
            session.add(v)

        session.commit()
        print("SQL seed complete")
    finally:
        session.close()


def seed_mongo(retries: int = 5, delay: int = 2):
    initialize_mongo()
    if mongo_database is None:
        raise RuntimeError("MongoDB not initialized")

    collection = mongo_database["telemetrias"]
    collection.delete_many({})

    docs = []
    for item in TELEMETRIA_SEED:
        docs.append(
            {
                "veiculo_id": item["veiculo_id"],
                "location": item["location"],
                "temperatura": item["temperatura"],
                "velocidade": item["velocidade"],
                "timestamp": item["timestamp"],
            }
        )

    attempt = 0
    while attempt < retries:
        try:
            if docs:
                collection.insert_many(docs)
            print("Mongo seed complete")
            return
        except PyMongoError as e:
            attempt += 1
            print(f"Mongo insert failed (attempt {attempt}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("Failed to seed MongoDB after retries")


if __name__ == "__main__":
    print("Starting seed...")
    seed_sql()
    seed_mongo()
    print("Seeding finished")
