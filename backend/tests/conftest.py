

import os
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError


@pytest.fixture(scope="session")
def mongo_server_uri():
    uri = os.getenv("TEST_MONGODB_URI", "mongodb://127.0.0.1:27018")

    with MongoClient(uri, serverSelectionTimeoutMS=5000) as connection:
        try:
            connection.admin.command("ping")
        except PyMongoError:
            pytest.fail(
                "MongoDB de testes indisponivel. Na raiz do projeto, execute "
                "'docker compose -f docker-compose.test.yml up -d mongo-test'. "
                "Padrao: localhost:27018; ajuste TEST_MONGODB_URI se necessario.",
                pytrace=False,
            )
    return uri


@pytest.fixture
def client(tmp_path, monkeypatch, mongo_server_uri):
    from app.database import mongo, sql
    from app.main import app
    from app.models import MotoristaModel, VeiculoModel
    from app.services.telemetria import conexoes

    database_name = f"geolog_pytest_{uuid4().hex}"
    parts = urlsplit(mongo_server_uri)
    test_uri = urlunsplit(parts._replace(path=f"/{database_name}"))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    monkeypatch.setenv("MONGODB_URI", test_uri)
    monkeypatch.setattr(sql, "engine", None)
    monkeypatch.setattr(sql, "SessionLocal", None)
    monkeypatch.setattr(mongo, "mongo_client", None)
    monkeypatch.setattr(mongo, "mongo_database", None)
  
    conexoes.clear()

    try:

        with TestClient(app) as test_client:
            with sql.create_session() as session:
                session.add_all([
                    MotoristaModel(id=1, nome="Carlos Andrade", cnh="123456789", status="Ativo"),
                    MotoristaModel(id=2, nome="Mariana Silva", cnh="987654321", status="Ativo"),
                    MotoristaModel(id=3, nome="Roberto Souza", cnh="456789123", status="Em Descanso"),
                ])
                session.flush()
                session.add_all([
                    VeiculoModel(id=101, placa="ABC-1A23", modelo="Volvo FH 540", motorista_id=1),
                    VeiculoModel(id=102, placa="XYZ-9876", modelo="Scania R450", motorista_id=2),
                    VeiculoModel(id=103, placa="KGB-4567", modelo="Mercedes Actros", motorista_id=3),
                ])
                session.commit()

            timestamp = datetime(2026, 9, 11, 10, tzinfo=timezone.utc)
            mongo.mongo_database["telemetrias"].insert_many([
                {"veiculo_id": 101, "location": {"type": "Point", "coordinates": [-34.873, -7.115]},
                 "temperatura": 4.2, "velocidade": 65, "timestamp": timestamp},
                {"veiculo_id": 102, "location": {"type": "Point", "coordinates": [-34.832, -7.121]},
                 "temperatura": -18.5, "velocidade": 85, "timestamp": timestamp},
                {"veiculo_id": 103, "location": {"type": "Point", "coordinates": [-34.950, -7.150]},
                 "temperatura": 22.0, "velocidade": 0, "timestamp": timestamp},
            ])
            yield test_client
    finally:
        conexoes.clear()
        if mongo.mongo_client is not None:

            try:
                mongo.mongo_client.drop_database(database_name)
            finally:
                mongo.mongo_client.close()
        if sql.engine is not None:
            sql.engine.dispose()


@pytest.fixture
def collection(client):
    from app.database import mongo
    return mongo.mongo_database["telemetrias"]


@pytest.fixture
def telemetry_payload():
    return {
        "location": {"latitude": -7.116, "longitude": -34.874},
        "temperatura": 5.5,
        "velocidade": 70,
        "veiculo_id": 101,
        "timestamp": "2026-10-01T22:00:00Z",
    }


@pytest.fixture
def nearby_params():
    return {"latitude": -7.115, "longitude": -34.873, "raio": 1, "socket_id": uuid4().hex}


@pytest.fixture
def connected_socket(client, nearby_params):
    with client.websocket_connect(
        f"/api/v1/telemetrias/ws?socket_id={nearby_params['socket_id']}"
    ) as websocket:
        yield websocket
