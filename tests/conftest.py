import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


@pytest.fixture()
def client(monkeypatch):
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Give each test its own "Cassandra" log file so runs don't leak into each other.
    log_fd, log_path = tempfile.mkstemp(suffix=".json")
    os.close(log_fd)
    os.remove(log_path)  # nosql_store creates it fresh on first write
    monkeypatch.setattr("app.nosql_store.NOSQL_LOG_PATH", log_path)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    os.close(db_fd)
    os.remove(db_path)
    if os.path.exists(log_path):
        os.remove(log_path)
