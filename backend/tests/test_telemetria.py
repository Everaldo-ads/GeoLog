from datetime import datetime

import pytest

pytestmark = pytest.mark.integration


def test_listar_telemetrias_join_poliglota(client):
    response = client.get("/api/v1/telemetrias")
    assert response.status_code == 200
    por_veiculo = {item["veiculo"]["id"]: item for item in response.json()}
    assert set(por_veiculo) == {101, 102, 103}
    item = por_veiculo[101]
    assert item["temperatura"] == 4.2
    assert item["velocidade"] == 65
    assert item["location"] == {"latitude": -7.115, "longitude": -34.873}
    assert item["veiculo"]["placa"] == "ABC-1A23"
    assert item["veiculo"]["motorista"]["nome"] == "Carlos Andrade"


def test_criar_telemetria_persiste_geojson(client, collection, telemetry_payload):
    response = client.post("/api/v1/telemetrias", json=telemetry_payload)
    assert response.status_code == 201
    item = response.json()
    assert item["temperatura"] == 5.5
    assert item["veiculo"]["id"] == 101
    assert item["location"] == telemetry_payload["location"]
    document = collection.find_one({"veiculo_id": 101, "temperatura": 5.5})
    assert document is not None
    assert document["location"] == {"type": "Point", "coordinates": [-34.874, -7.116]}
    assert isinstance(document["timestamp"], datetime)
    assert document["timestamp"] == datetime(2026, 10, 1, 22)
    assert "veiculo" not in document
    assert collection.count_documents({}) == 4
    assert any(t["temperatura"] == 5.5 for t in client.get("/api/v1/telemetrias").json())


def test_telemetria_com_veiculo_inexistente(client, collection, telemetry_payload):
    telemetry_payload["veiculo_id"] = 999
    response = client.post("/api/v1/telemetrias", json=telemetry_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Veículo não encontrado"
    assert collection.count_documents({}) == 3


@pytest.mark.parametrize("campo,valor", [("velocidade", -1), ("veiculo_id", 0), ("timestamp", "invalido")])
def test_telemetria_invalida(client, collection, telemetry_payload, campo, valor):
    telemetry_payload[campo] = valor
    assert client.post("/api/v1/telemetrias", json=telemetry_payload).status_code == 422
    assert collection.count_documents({}) == 3


def test_indices_criados_no_startup(collection):
    indices = collection.index_information()
    assert indices["location_2dsphere"]["key"] == [("location", "2dsphere")]
    assert indices["veiculo_timestamp_desc"]["key"] == [("veiculo_id", 1), ("timestamp", -1)]


def test_ultima_telemetria_por_timestamp(client, collection, telemetry_payload):
    from app.routers.telemetria import telemetria_repository

    assert client.post("/api/v1/telemetrias", json=telemetry_payload).status_code == 201
    telemetry_payload.update(temperatura=99, timestamp="2026-09-01T10:00:00Z")
    assert client.post("/api/v1/telemetrias", json=telemetry_payload).status_code == 201
    ultima = telemetria_repository.get_last_telemetry(101)
    assert ultima.temperatura == 5.5
    assert telemetria_repository.get_last_telemetry(999) is None
