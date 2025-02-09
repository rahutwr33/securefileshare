import pytest
from fastapi import status
from app.models.user import UserRole
import base64
from app.utils.auth import create_access_token, get_current_user
from datetime import timedelta
import jwt
from app.config import settings

@pytest.fixture
def admin_token(test_admin):
    # Create a fresh token with full admin credentials
    access_token = create_access_token(
        data={
            "sub": test_admin.email,
            "role": UserRole.ADMIN.value,
            "is_active": True,
            "id": test_admin.id
        },
        expires_delta=timedelta(minutes=30)
    )
    
    # Debug: Verify token contents
    try:
        decoded = jwt.decode(
            access_token, 
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        print(f"Decoded admin token: {decoded}")
    except Exception as e:
        print(f"Token decode error: {e}")
    
    return access_token

# Admin User Management Tests
def test_admin_get_users_list(admin_client, test_user):
    response = admin_client.get("/api/admin/users")
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.json() if response.status_code != 204 else ''}")
    
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) >= 1
    assert any(user["email"] == test_user.email for user in users)

def test_admin_delete_user(admin_client, test_user):
    response = admin_client.delete(f"/api/admin/users/{test_user.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_admin_delete_admin_user(admin_client, test_admin):
    response = admin_client.delete(
        f"/api/admin/users/{test_admin.id}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_non_admin_access_denied(auth_client):
    response = auth_client.get("/api/admin/users")
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Admin File Management Tests
def test_admin_delete_file(admin_client, test_uploaded_file):
    print(f"Starting admin delete file test")
    print(f"File data: {test_uploaded_file}")
    
    # Verify we have a file ID
    file_id = test_uploaded_file.get('id')
    if not file_id:
        print("Available fields in response:", test_uploaded_file.keys())
        raise AssertionError(f"No file ID found in response: {test_uploaded_file}")
    
    # Try to delete the file
    delete_url = f"/api/admin/file/{file_id}"
    print(f"Attempting to delete file at: {delete_url}")
    
    response = admin_client.delete(delete_url)
    print(f"Delete response status: {response.status_code}")
    print(f"Delete response headers: {response.headers}")
    print(f"Delete response body: {response.text if response.text else 'No response body'}")
    
    if response.status_code != status.HTTP_204_NO_CONTENT:
        print(f"Delete failed with status {response.status_code}")
        if response.text:
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw error response: {response.text}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.fixture
def test_uploaded_file(admin_client, mock_encryption_params):
    file_content = b"Test file content"
    mock_key = base64.b64encode(b"A" * 32).decode()
    mock_iv = base64.b64encode(b"B" * 16).decode()
    
    files = {"file": ("test.txt", file_content, "text/plain")}
    data = {
        "iv": mock_iv,
        "user_key": mock_key
    }
    
    # First, try to upload the file
    upload_response = admin_client.post(
        "/api/user/upload",
        files=files,
        data=data
    )
    print(f"Upload response status: {upload_response.status_code}")
    print(f"Upload response headers: {upload_response.headers}")
    print(f"Upload response body: {upload_response.text}")
    
    assert upload_response.status_code == status.HTTP_200_OK, f"Upload failed with status {upload_response.status_code}"
    
    try:
        upload_data = upload_response.json()
    except Exception as e:
        print(f"Failed to parse upload response as JSON: {e}")
        print(f"Raw response: {upload_response.text}")
        raise
    
    print(f"Upload data: {upload_data}")
    return upload_data

@pytest.fixture
def mock_encryption_params():
    return {
        "iv": base64.b64encode(b"A" * 16).decode(),
        "user_key": base64.b64encode(b"B" * 32).decode()
    } 