import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
import os
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash, create_access_token
from datetime import timedelta
import jwt
from app.config import settings

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    # Create the test database and tables
    Base.metadata.create_all(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        # Clean up after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db
    
    # Configure test client
    client = TestClient(
        app,
        base_url="https://testserver",  # Use HTTPS
    )
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(test_db):
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword123!"),
        role=UserRole.USER
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(test_db):
    admin = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=get_password_hash("adminpassword123!"),
        role=UserRole.ADMIN
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def test_user_token(test_user):
    access_token = create_access_token(
        data={
            "sub": test_user.email,
            "role": UserRole.USER.value,
            "id": test_user.id,
            "is_active": True
        },
        expires_delta=timedelta(minutes=30)
    )
    return access_token

@pytest.fixture
def test_admin_token(test_admin):
    print(f"Creating admin token for: {test_admin.email}")
    print(f"Admin role: {test_admin.role}")
    print(f"Admin ID: {test_admin.id}")
    
    access_token = create_access_token(
        data={
            "sub": test_admin.email,
            "role": UserRole.ADMIN.value,
            "id": test_admin.id,
            "is_active": True,
            "type": "access_token"
        },
        expires_delta=timedelta(minutes=30)
    )
    return access_token

@pytest.fixture
def auth_client(client, test_user_token):
    # Set the auth cookie
    client.cookies.set("access_token", test_user_token)
    return client

@pytest.fixture
def admin_client(client, test_admin_token):
    # Set the auth cookie
    client.cookies.set("access_token", test_admin_token)
    return client

# Keep these for backward compatibility
@pytest.fixture
def auth_headers(test_user_token):
    return {"Authorization": f"Bearer {test_user_token}"}

@pytest.fixture
def admin_auth_headers(test_admin_token):
    return {"Authorization": f"Bearer {test_admin_token}"} 