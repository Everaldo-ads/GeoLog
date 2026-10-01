import pytest

pytestmark = pytest.mark.integration


def test_websocket_recebe_telemetria_com_timestamp(
    client, connected_socket, nearby_params, telemetry_payload
):
    response = client.get("/api/v1/veiculos/proximos", params=nearby_params)
    assert response.status_code == 200
    response = client.post("/api/v1/telemetrias", json=telemetry_payload)
    assert response.status_code == 201
    # O timeout do pytest impede espera infinita se o envio parar de funcionar.
    message = connected_socket.receive_json()
    assert message == response.json()
    assert message["timestamp"] == "2026-10-01T22:00:00Z"
    assert message["veiculo"]["motorista"]["nome"] == "Carlos Andrade"


def test_websocket_filtra_ponto_fora_do_raio(
    client, connected_socket, nearby_params, telemetry_payload
):
    assert client.get("/api/v1/veiculos/proximos", params=nearby_params).status_code == 200
    fora = dict(telemetry_payload, location={"latitude": 0, "longitude": 0}, temperatura=99)
    assert client.post("/api/v1/telemetrias", json=fora).status_code == 201
    assert client.post("/api/v1/telemetrias", json=telemetry_payload).status_code == 201
    assert connected_socket.receive_json()["temperatura"] == 5.5


def test_desconectar_remove_sessao(client, nearby_params):
    from app.services.telemetria import conexoes

    socket_id = nearby_params["socket_id"]
    with client.websocket_connect(f"/api/v1/telemetrias/ws?socket_id={socket_id}"):
        assert client.get("/api/v1/veiculos/proximos", params=nearby_params).status_code == 200
        assert socket_id in conexoes
    assert socket_id not in conexoes
