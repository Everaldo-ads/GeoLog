from dotenv import load_dotenv
from fastapi import FastAPI

from . import models
from .database.mongo import initialize_mongo
from .database.sql import Base, initialize_sql
from .routers import motoristas, telemetrias, veiculos

app = FastAPI(title="GeoLog API", version="0.1.0")
app.include_router(motoristas.router)
app.include_router(veiculos.router)
app.include_router(telemetrias.router)


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
