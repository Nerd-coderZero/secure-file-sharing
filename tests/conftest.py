# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config_test import get_test_settings
from app.database import Base, get_db
from app.main import app as fastapi_app

# Get test settings
test_settings = get_test_settings()

# Create test database engine
SQLALCHEMY_DATABASE_URL = test_settings.DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Remove tables after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    # Dependency override
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Override the dependency
    fastapi_app.dependency_overrides[get_db] = override_get_db
    
    # Return test client
    with TestClient(fastapi_app) as c:
        yield c
