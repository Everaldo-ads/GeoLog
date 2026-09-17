import os
from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None


def initialize_sql() -> Engine:
    global engine, SessionLocal
    database_url = os.getenv("DATABASE_URL", "sqlite:///./logitech.db")
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
        if database_url.startswith("sqlite")
        else {},
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine


def get_sql_session() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("SQL database has not been initialized")
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
