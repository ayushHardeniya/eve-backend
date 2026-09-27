import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "postgresql+psycopg://eve:eve@localhost:5433/eve"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
