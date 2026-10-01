# Testes automatizados do GeoLog

A suite usa pytest + TestClient do FastAPI, SQLite temporario e MongoDB real.
Nao e necessario iniciar a API, o frontend ou executar seed.py.

## Opcao 1: executar tudo com Docker (mais simples)

Requisito: Docker Desktop instalado e aberto, com suporte a Docker Compose.
Extraia o ZIP e abra um terminal na pasta que contem docker-compose.test.yml.
Execute:

```powershell
docker compose -f docker-compose.test.yml up --abort-on-container-exit --exit-code-from tests
```

Esse comando inicia um MongoDB separado, instala as dependencias de teste em
um container Python e executa `python -m pytest -v`. A primeira execucao pode
demorar para baixar as imagens e dependencias. O codigo de saida sera zero
quando todos os testes passarem; falhas retornam um codigo diferente de zero.
O Compose de testes e independente do docker-compose.yml do aplicativo.

Ao terminar, remova os containers de teste:

```powershell
docker compose -f docker-compose.test.yml down
```

## Opcao 2: executar pytest pelo Python no Windows

Requisitos: Python 3.10 ou superior e MongoDB 7.0. A validacao deste pacote usa
Python 3.12 e MongoDB 7.0.16. Voce pode iniciar so o Mongo pelo Docker, estando
na raiz do projeto:

```powershell
docker compose -f docker-compose.test.yml up -d --wait mongo-test
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe -m pytest -v
```

Nao precisa ativar o ambiente virtual nem criar um arquivo .env.
No Linux/macOS, use `python3 -m venv .venv` e `.venv/bin/python` no lugar dos
comandos `py` e `.\.venv\Scripts\python.exe`.

Se voce ja tiver MongoDB em outra porta, defina o servidor de testes no
PowerShell antes de rodar pytest:

```powershell
$env:TEST_MONGODB_URI = "mongodb://127.0.0.1:27017"
.\.venv\Scripts\python.exe -m pytest -v
```

O padrao e `mongodb://127.0.0.1:27018`. Em Linux/macOS:

```bash
TEST_MONGODB_URI=mongodb://127.0.0.1:27017 .venv/bin/python -m pytest -v
```

Se a conexao exigir autenticacao, informe usuario, senha e `authSource` na URI.
Use um usuario autorizado a criar/remover bancos de teste.

## Como os dados ficam isolados

- Cada teste de integracao usa um SQLite dentro da pasta temporaria do pytest.
- Cada teste cria um MongoDB chamado `geolog_pytest_<uuid>`, com nome unico.
- O startup real da API cria os indices. A fixture adiciona tres motoristas,
  tres veiculos e tres telemetrias conhecidos.
- Ao terminar, a fixture remove exclusivamente o banco Mongo que ela criou e
  fecha suas conexoes, inclusive quando um teste falha.
- O nome de banco eventualmente presente em TEST_MONGODB_URI e substituido
  pelo nome aleatorio. MONGODB_URI e DATABASE_URL do aplicativo nao sao usados.

Se o MongoDB estiver indisponivel, os testes de integracao reportam erro de
preparacao; eles nao sao ignorados silenciosamente.

## O que e verificado

| Arquivo em backend/tests | Verificacao |
| --- | --- |
| test_api.py | Health, listar/buscar/criar motoristas e veiculos, persistencia SQLite, vinculo motorista/veiculo, respostas 404 e validacoes 422 |
| test_telemetria.py | Join SQLite/Mongo, gravacao GeoJSON em longitude/latitude, timestamp BSON, indices 2dsphere e veiculo/timestamp, telemetria mais recente e erros |
| test_geoespacial.py | Consulta real com $geoNear, raios 0/1/5/10 km, area vazia, sessao ausente, um ponto por veiculo e exclusao de posicoes antigas dentro do raio |
| test_websocket.py | Conexao real via TestClient, envio de telemetria com timestamp, filtro por raio e remocao da sessao ao desconectar |
| test_geolocation.py | Distancia zero e distancia em quilometros; estes dois testes dispensam MongoDB |

O mapa, os graficos e os cliques na interface React precisam de verificacao
visual ou de uma suite propria de frontend. O pytest deste pacote cobre o backend.

## Executar apenas parte da suite

Dentro de backend, com o Python do ambiente virtual:

```powershell
# Somente os dois testes que dispensam MongoDB
.\.venv\Scripts\python.exe -m pytest -v -m "not integration"

# Somente busca geoespacial
.\.venv\Scripts\python.exe -m pytest -v tests/test_geoespacial.py

# Somente WebSocket
.\.venv\Scripts\python.exe -m pytest -v tests/test_websocket.py

# Mostrar detalhes de uma falha
.\.venv\Scripts\python.exe -m pytest -v --tb=short
```

`PASSED` indica teste aprovado; `FAILED` indica comportamento diferente do
esperado; `ERROR` indica problema na preparacao, como MongoDB sem conexao.
Ha um limite de 30 segundos por teste para detectar travamentos de WebSocket.

## Arquivos adicionados

- backend/requirements-test.txt
- backend/pytest.ini
- backend/tests/
- docker-compose.test.yml
- TESTES.md

## Correcao encontrada pelos testes

Em backend/app/services/telemetria.py, o envio WebSocket agora usa
`telemetria.model_dump(mode="json")`. Antes, `model_dump()` mantinha o timestamp
como datetime e `send_json()` lancava `TypeError: Object of type datetime is
not JSON serializable`. A correcao transforma a data em texto ISO 8601 somente
na mensagem enviada. A persistencia MongoDB continua usando timestamp BSON.

## Resultado da validacao

Em 01/10/2026: **38 testes aprovados**, sem falhas ou testes ignorados, usando
Python 3.12.14, pytest 8.3.5 e MongoDB real 7.0.16. A suite foi executada nos
dois backends enviados. Os avisos de descontinuacao de startup/TestClient nao
impediram a execucao. A limpeza dos bancos de teste tambem foi conferida.

O comando Docker esta configurado neste pacote; a validacao aqui foi feita
diretamente pelo Python, pois Docker nao esta disponivel neste ambiente.
