import pytest

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("raio,esperados", [(0, [101]), (1, [101]), (5, [101, 102]), (10, [101, 102, 103])])
def test_busca_por_raio_real_no_mongo(client, connected_socket, nearby_params, raio, esperados):
    nearby_params["raio"] = raio
    response = client.get("/api/v1/veiculos/proximos", params=nearby_params)
    assert response.status_code == 200
    assert [t["veiculo"]["id"] for t in response.json()] == esperados


def test_busca_em_regiao_sem_veiculos(client, connected_socket, nearby_params):
    nearby_params.update(latitude=0, longitude=0)
    response = client.get("/api/v1/veiculos/proximos", params=nearby_params)
    assert response.status_code == 200
    assert response.json() == []


def test_busca_sem_conexao_websocket(client, nearby_params):
    response = client.get("/api/v1/veiculos/proximos", params=nearby_params)
    assert response.status_code == 404
    assert response.json()["detail"] == "Conexão WebSocket não encontrada"


def test_veiculo_que_saiu_do_raio_nao_aparece_por_ponto_antigo(
    client, connected_socket, nearby_params, collection
):
    novo = {"location": {"latitude": 0, "longitude": 0}, "temperatura": 10,
            "velocidade": 50, "veiculo_id": 101, "timestamp": "2026-10-01T22:00:00Z"}
    assert client.post("/api/v1/telemetrias", json=novo).status_code == 201
    response = client.get("/api/v1/veiculos/proximos", params=nearby_params)
    assert response.status_code == 200
    assert response.json() == []


def test_busca_retorna_um_ponto_por_veiculo(client, connected_socket, nearby_params, telemetry_payload):
    assert client.post("/api/v1/telemetrias", json=telemetry_payload).status_code == 201
    response = client.get("/api/v1/veiculos/proximos", params=nearby_params)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["temperatura"] == 5.5
