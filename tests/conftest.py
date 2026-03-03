import sys
from pathlib import Path
from collections.abc import Generator, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Ensure tests can import project modules (models, auth, routers, etc.).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import models
from auth import get_current_user
from database import Base, get_db
from main import app


TEST_DATABASE_URL = "sqlite:///./test.db"

# Keep SQLite behavior compatible with FastAPI test execution.
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    # Start every test from a clean schema state.
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def fake_current_user() -> models.User:
    return models.User(
        id=1,
        username="test-user",
        email="test@example.com",
        hashed_password="fake-hash",
    )


@pytest.fixture(scope="function")
def app_with_overrides(db_session: Session, fake_current_user: models.User):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        return fake_current_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def app_without_auth_override(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield app
    finally:
        app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer fake-jwt-token"}


@pytest_asyncio.fixture(scope="function")
async def async_client(app_with_overrides) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app_with_overrides)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def async_client_no_auth_override(app_without_auth_override) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app_without_auth_override)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
