from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    region_id: str
    severity: str
    message: str


class Annotation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    region_id: str
    source: str
    text: str
    agrees_with_ai: bool = True


engine = None


def get_engine(database_url: str):
    global engine
    if engine is None:
        engine = create_engine(database_url, echo=False)
    return engine


def create_db_and_tables(database_url: str) -> None:
    eng = get_engine(database_url)
    SQLModel.metadata.create_all(eng)


def get_session() -> Session:
    if engine is None:
        raise RuntimeError("Engine not initialized")
    return Session(engine)

