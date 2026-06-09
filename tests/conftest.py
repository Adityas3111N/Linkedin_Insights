import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models.base import Base

# Setup a clean in-memory SQLite database for unit and integration testing
# StaticPool prevents SQLite from closing the connection and dropping tables between tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="db_session", scope="function")
def fixture_db_session():
    """Fixture to create and clean up a test database session for each test case."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client", scope="function")
def fixture_client(db_session):
    """Fixture to provide a FastAPI TestClient with database dependencies overridden."""
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    # Override the regular app dependency with our test database session
    app.dependency_overrides[get_db] = _get_test_db
    # Clear the page router cache so tests don't share state
    from app.routers.page_router import _details_cache
    _details_cache.clear()
    with TestClient(app) as test_client:
        yield test_client
    # Clear overrides after the test completes
    app.dependency_overrides.clear()
