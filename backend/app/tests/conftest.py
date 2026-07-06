import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

os.environ.setdefault("DEFAULT_LLM_PROVIDER", "mock")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_social_growth_lab.db")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

TEST_DB_URL = "sqlite:///./test_social_growth_lab.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_social_growth_lab.db"):
        os.remove("./test_social_growth_lab.db")


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    register_resp = client.post("/auth/register", json={"username": "testuser", "password": "testpass123"})
    if register_resp.status_code == 400:
        # user already exists from a previous test in this session - fine, just log in.
        pass
    resp = client.post("/auth/login", json={"username": "testuser", "password": "testpass123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
