import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base
from app.core.dependencies import get_db
from app.main import app
from app.models import VolanteORM

SEED_NAMES = (
    "VCS-26-131000-00167",
    "VCS-26-131000-00168",
    "VCS-26-142000-00010",
)

engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine_test, autocommit=False, autoflush=False)


@pytest.fixture
def client() -> TestClient:
    """Sesión SQLite en memoria y TestClient sobre el router real."""
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    for name in SEED_NAMES:
        db.add(VolanteORM(name=name))
    db.commit()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine_test)
