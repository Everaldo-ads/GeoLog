from dotenv import load_dotenv
from fastapi import FastAPI

from .database.mongo import initialize_mongo
from .database.sql import Base, initialize_sql
from .routers import motorista, telemetria, veiculo

app = FastAPI(title="GeoLog API", version="0.1.0")
app.include_router(motorista.router)
app.include_router(veiculo.router)
app.include_router(telemetria.router)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def initialize_database() -> None:
    load_dotenv()
    engine = initialize_sql()
    initialize_mongo()
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao GeoLog API"}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "backend"}


@app.get("/api/v1/ping")
def ping():
    return {"pong": True}
