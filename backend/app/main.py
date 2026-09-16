from fastapi import FastAPI

app = FastAPI(title="GeoLog API", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao GeoLog API"}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "backend"}


@app.get("/api/v1/ping")
def ping():
    return {"pong": True}
