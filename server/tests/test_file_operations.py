import pytest
from fastapi import status
import io
from app.models.file import SharePermission
import base64
import time

@pytest.fixture
def mock_encryption_params():
    return {
        "iv": base64.b64encode(b"A" * 16).decode(),
        "user_key": base64.b64encode(b"B" * 32).decode()
    }

@pytest.fixture
def test_file_upload_response(auth_client, mock_encryption_params):
    file_content = b"Test file content"
    file = io.BytesIO(file_content)
    
    files = {"file": ("test.txt", file, "text/plain")}
    data = mock_encryption_params
    
    response = auth_client.post(
        "/api/user/upload",
        files=files,
        data=data
    )
    print(f"Upload response: {response.status_code}, {response.json() if response.status_code != 204 else ''}")
    assert response.status_code == status.HTTP_200_OK
    return response.json()

def test_upload_file_success(auth_client, mock_encryption_params):
    file_content = b"Test file content"
    file = io.BytesIO(file_content)
    
    response = auth_client.post(
        "/api/user/upload",
        files={"file": ("test.txt", file, "text/plain")},
        data=mock_encryption_params
    )
    print(f"Upload response: {response.status_code}, {response.json() if response.status_code != 204 else ''}")
    assert response.status_code == status.HTTP_200_OK

def test_upload_file_no_auth(client):
    file = io.BytesIO(b"Test content")
    response = client.post(
        "/api/user/upload",
        files={"file": ("test.txt", file, "text/plain")}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_upload_large_file(auth_client, mock_encryption_params):
    large_content = b"0" * (6 * 1024 * 1024)
    file = io.BytesIO(large_content)
    
    response = auth_client.post(
        "/api/user/upload",
        files={"file": ("large.txt", file, "text/plain")},
        data=mock_encryption_params
    )
    print(f"Large file upload response: {response.status_code}, {response.json() if response.status_code != 204 else ''}")
    assert response.status_code == status.HTTP_200_OK

# File Download Tests
def test_download_file_success(auth_client, test_file_upload_response):
    response = auth_client.get(
        f"/api/user/download/{test_file_upload_response['id']}"
    )
    print(f"Download response: {response.status_code}, {response.json() if response.status_code != 204 else ''}")
    assert response.status_code == status.HTTP_200_OK

def test_download_nonexistent_file(auth_client):
    response = auth_client.get("/api/user/download/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# File Sharing Tests
@pytest.fixture
def test_file_share(auth_client, test_file_upload_response, test_user, test_db):
    test_user = test_db.merge(test_user)
    
    share_data = {
        "file_id": test_file_upload_response["id"],
        "user_id": test_user.id,
        "expires_in_seconds": 3600,
        "permission": "view"
    }
    print(f"Creating share with data: {share_data}")
    
    response = auth_client.post(
        "/api/user/share",
        json=share_data
    )
    print(f"Share creation response: {response.status_code}")
    print(f"Share creation body: {response.json() if response.status_code != 204 else ''}")
    
    assert response.status_code == status.HTTP_200_OK
    share_data = response.json()
    print(f"Final share data: {share_data}")
    
    # Wait for share to be created
    time.sleep(1)
    
    return share_data

def test_access_shared_file(client, test_file_share):
    print(f"Share data: {test_file_share}")
    # Extract share ID from the share_link URL
    share_link = test_file_share['share_link']
    share_id = share_link.split('/')[-2]  # Get the ID from the URL
    
    response = client.get(f"/api/user/shared/{share_id}")
    print(f"Access response: {response.status_code}")
    print(f"Access response body: {response.json() if response.status_code != 204 else ''}")
    assert response.status_code == status.HTTP_200_OK

@pytest.fixture
def test_expired_share(auth_client, test_file_upload_response, test_user, test_db):
    # Refresh test_user from the database to ensure it's attached to a session
    test_user = test_db.merge(test_user)
    
    share_response = auth_client.post(
        "/api/user/share",
        json={
            "file_id": test_file_upload_response['id'],
            "user_id": test_user.id,
            "expires_in_seconds": -3600,  # Expired 1 hour ago
            "permission": "view"
        }
    )
    assert share_response.status_code == status.HTTP_200_OK
    return share_response.json()

def test_access_expired_share(client, test_expired_share):
    share_link = test_expired_share['share_link']
    share_id = share_link.split('/')[-2]  # Get the ID from the URL
    
    response = client.get(f"/api/user/shared/{share_id}")
    assert response.status_code == status.HTTP_410_GONE 