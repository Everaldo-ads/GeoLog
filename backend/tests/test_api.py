import pytest

pytestmark = pytest.mark.integration


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "backend"}


def test_listar_motoristas(client):
    response = client.get("/api/v1/motoristas")
    assert response.status_code == 200
    por_id = {item["id"]: item for item in response.json()}
    assert set(por_id) == {1, 2, 3}
    assert por_id[1]["nome"] == "Carlos Andrade"
    assert por_id[3]["status"] == "Em Descanso"


def test_buscar_motorista(client):
    response = client.get("/api/v1/motoristas/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1, "nome": "Carlos Andrade", "cnh": "123456789", "status": "Ativo"
    }


@pytest.mark.parametrize("endpoint,detail", [
    ("motoristas/999", "Motorista não encontrado"),
    ("veiculos/999", "Veículo não encontrado"),
])
def test_buscar_id_inexistente(client, endpoint, detail):
    response = client.get(f"/api/v1/{endpoint}")
    assert response.status_code == 404
    assert response.json()["detail"] == detail


def test_criar_motorista_persiste_no_sqlite(client):
    from app.database import sql
    from app.models import MotoristaModel

    response = client.post("/api/v1/motoristas", json={
        "nome": "João Silva", "cnh": "111222333", "status": "Ativo"
    })
    assert response.status_code == 201
    motorista = response.json()
    assert client.get(f"/api/v1/motoristas/{motorista['id']}").json() == motorista
    with sql.create_session() as session:
        registro = session.get(MotoristaModel, motorista["id"])
        assert registro.nome == "João Silva"
        assert registro.cnh == "111222333"


@pytest.mark.parametrize("campo", ["nome", "cnh", "status"])
def test_motorista_com_campo_vazio(client, campo):
    payload = {"nome": "João", "cnh": "111222333", "status": "Ativo"}
    payload[campo] = ""
    assert client.post("/api/v1/motoristas", json=payload).status_code == 422
    assert len(client.get("/api/v1/motoristas").json()) == 3


def test_listar_veiculos_com_motoristas(client):
    response = client.get("/api/v1/veiculos")
    assert response.status_code == 200
    por_id = {item["id"]: item for item in response.json()}
    assert set(por_id) == {101, 102, 103}
    assert por_id[101]["placa"] == "ABC-1A23"
    assert por_id[101]["motorista"]["nome"] == "Carlos Andrade"


def test_buscar_veiculo(client):
    response = client.get("/api/v1/veiculos/101")
    assert response.status_code == 200
    assert response.json()["modelo"] == "Volvo FH 540"
    assert response.json()["motorista"]["id"] == 1


def test_filtrar_veiculos_por_motorista(client):
    response = client.get("/api/v1/veiculos/motorista/2")
    assert response.status_code == 200
    assert [v["id"] for v in response.json()] == [102]
    assert client.get("/api/v1/veiculos/motorista/999").json() == []


def test_criar_veiculo_persiste_relacao(client):
    from app.database import sql
    from app.models import VeiculoModel

    response = client.post("/api/v1/veiculos", json={
        "placa": "AAA-1B23", "modelo": "Ford Cargo", "motorista_id": 1
    })
    assert response.status_code == 201
    veiculo = response.json()
    assert veiculo["motorista"]["id"] == 1
    assert client.get(f"/api/v1/veiculos/{veiculo['id']}").json() == veiculo
    with sql.create_session() as session:
        registro = session.get(VeiculoModel, veiculo["id"])
        assert registro.placa == "AAA-1B23"
        assert registro.motorista_id == 1


def test_criar_veiculo_com_motorista_inexistente(client):
    response = client.post("/api/v1/veiculos", json={
        "placa": "AAA-9999", "modelo": "Teste", "motorista_id": 999
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Motorista não encontrado"
    assert len(client.get("/api/v1/veiculos").json()) == 3


@pytest.mark.parametrize("campo,valor", [("placa", ""), ("modelo", ""), ("motorista_id", 0)])
def test_veiculo_invalido(client, campo, valor):
    payload = {"placa": "AAA-1B23", "modelo": "Teste", "motorista_id": 1}
    payload[campo] = valor
    assert client.post("/api/v1/veiculos", json=payload).status_code == 422
