# tests/test_auth.py
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.auth.models import User, UserRole
from app.utils.security import get_password_hash

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test users
    db = TestingSessionLocal()
    ops_user = User(
        email="ops@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.OPS,
        is_active=True
    )
    client_user = User(
        email="client@example.com",
        hashed_password=get_password_hash("password"),
        role=UserRole.CLIENT,
        is_active=True
    )
    db.add(ops_user)
    db.add(client_user)
    db.commit()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

def test_signup():
    response = client.post(
        "/auth/signup",
        json={"email": "newuser@example.com", "password": "password"}
    )
    assert response.status_code == 201
    assert "User created" in response.json()["message"]

def test_login_ops_user():
    response = client.post(
        "/auth/login",
        data={"username": "ops@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_client_user():
    response = client.post(
        "/auth/login",
        data={"username": "client@example.com", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()