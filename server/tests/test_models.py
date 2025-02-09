import pytest
from datetime import datetime, timedelta
from app.models.user import User, UserRole
from app.models.file import File
from app.models.share import FileShare
from app.models.verification import LoginVerification

def test_user_model(test_db):
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed",
        role=UserRole.USER
    )
    test_db.add(user)
    test_db.commit()
    
    assert user.id is not None
    assert user.is_user() == True
    assert user.is_admin() == False

def test_file_model(test_db, test_user):
    file = File(
        filename="test.txt",
        stored_filename="stored_test.txt",
        file_path="/path/to/file",
        size=1024,
        owner_id=test_user.id
    )
    test_db.add(file)
    test_db.commit()
    
    assert file.id is not None
    assert file.owner.id == test_user.id

def test_file_share_model(test_db, test_user):
    # First create a file
    file = File(
        filename="test.txt",
        stored_filename="stored_test.txt",
        file_path="/path/to/file",
        size=1024,
        owner_id=test_user.id
    )
    test_db.add(file)
    test_db.commit()
    
    # Create share
    share = FileShare(
        file_id=file.id,
        shared_with_user_id=test_user.id,
        share_link="abc123",
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    test_db.add(share)
    test_db.commit()
    
    assert share.id is not None
    assert share.file.filename == "test.txt"

def test_verification_model(test_db, test_user):
    verification = LoginVerification(
        id="test_id",
        user_id=test_user.id,
        code="123456",
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    test_db.add(verification)
    test_db.commit()
    
    assert verification.is_expired() == False
    
    # Test expiration
    verification.expires_at = datetime.utcnow() - timedelta(minutes=1)
    test_db.commit()
    assert verification.is_expired() == True 