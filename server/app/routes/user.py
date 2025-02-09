from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import secrets
import os
from pathlib import Path
from ..database import get_db
from ..models.user import User
from ..models.file import File as FileModel, SharePermission
from ..schemas.file import FileResponse, FileCreate, ShareFileRequest
from ..utils.auth import get_current_user, get_current_active_user
from ..utils.encryption import FileEncryption
from datetime import datetime, timedelta
from ..models.share import FileShare
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from ..config import settings
from dotenv import load_dotenv
from ..schemas.user import UserBasicResponse
from ..utils.email import send_share_email
from io import BytesIO
load_dotenv()
router = APIRouter(
    tags=["User"]
)
# Create uploads directory inside app directory
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
# file_encryption = FileEncryption()
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Validate key lengths
SERVER_AES_KEY = base64.b64decode(os.getenv("SERVER_AES_KEY"))
if len(SERVER_AES_KEY) != 32:
    raise ValueError(f"SERVER_AES_KEY must be 32 bytes, got {len(SERVER_AES_KEY)}")

SERVER_AES_IV = base64.b64decode(os.getenv("SERVER_AES_IV"))
if len(SERVER_AES_IV) != 16:
    raise ValueError(f"SERVER_AES_IV must be 16 bytes, got {len(SERVER_AES_IV)}")

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    iv: str = Form(...),
    user_key: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle file upload with double encryption:
    1. Decrypt the client-side encrypted file (Web Crypto API AES-GCM)
    2. Re-encrypt with server-side AES-256-GCM
    3. Store the server-encrypted file
    """
    try:
        # Parse encryption metadata from client
        encrypted_data = await file.read()
        iv = base64.b64decode(iv)
        decoded_key = base64.b64decode(user_key)
        print(f"Received Base64 Key: {user_key}")
        print(f"Decoded Key Length: {len(decoded_key)} bytes")  # Should be 32
        print(f"Decoded Key: {decoded_key.hex()}")  # Print actual bytes

        # Decrypt client-side encryption
        cipher = AES.new(decoded_key, AES.MODE_GCM, nonce=iv)
        decrypted_data = cipher.decrypt(encrypted_data)

        # Use GCM mode with the correct nonce length
        server_cipher = AES.new(SERVER_AES_KEY, AES.MODE_GCM)  # Let it generate its own nonce
        re_encrypted_data, tag = server_cipher.encrypt_and_digest(decrypted_data)
        
        # Generate a secure random filename
        stored_filename = f"{secrets.token_hex(16)}_{file.filename}"
        save_path = UPLOAD_DIR / f"{file.filename}.enc"
        
        with open(save_path, "wb") as f:
            f.write(server_cipher.nonce)
            f.write(tag)
            f.write(re_encrypted_data)
        
        # Store file metadata in database
        db_file = FileModel(
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=str(save_path),  # Convert Path to string for database
            size=len(re_encrypted_data),
            owner_id=current_user.id,
            created_at=datetime.utcnow(),
            file_type=file.content_type
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return {
            "message": "File uploaded successfully",
            "filename": db_file.filename,
            "id": db_file.id,
            "size": db_file.size,
            "upload_date": db_file.created_at,
            "file_type": db_file.file_type
}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file upload: {str(e)}"
        )

@router.get("/files", response_model=List[FileResponse])
async def get_user_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all files owned by the current logged-in user, sorted by most recent first.
    If user has admin role, return all files in the system.
    """
    # Create base query
    query = db.query(FileModel)
    
    # Check if user has admin role
    is_admin = current_user.role == "admin"
    
    # If not admin, filter by user's files only
    if not is_admin:
        query = query.filter(FileModel.owner_id == current_user.id)
    
    # Get files sorted by creation date
    files = query.order_by(FileModel.created_at.desc()).all()
    
    return [
        {
            "filename": file.filename,
            "id": file.id,
            "size": file.size,
            "upload_date": file.created_at
        }
        for file in files
    ]

@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download and decrypt a file:
    1. Verify file ownership
    2. Read the encrypted file
    3. Return encrypted data with necessary decryption metadata
    """
    # Check file ownership
    file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Read the encrypted file
        with open(file.file_path, "rb") as f:
            # First 16 bytes are nonce, next 16 bytes are tag, rest is encrypted data
            nonce = f.read(16)
            tag = f.read(16)
            encrypted_data = f.read()
        
        # Create cipher for decryption
        cipher = AES.new(SERVER_AES_KEY, AES.MODE_GCM, nonce=nonce)
        
        # Decrypt the data
        decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)
        
        # Generate a new key and IV for client-side encryption
        client_key = secrets.token_bytes(32)
        client_iv = secrets.token_bytes(12)  # 12 bytes for GCM mode
        
        # Encrypt with the new key for transmission
        client_cipher = AES.new(client_key, AES.MODE_GCM, nonce=client_iv)
        re_encrypted_data, new_tag = client_cipher.encrypt_and_digest(decrypted_data)
        
        # Encode binary data for JSON response
        response_data = {
            "filename": file.filename,
            "encrypted_data": base64.b64encode(re_encrypted_data).decode('utf-8'),
            "key": base64.b64encode(client_key).decode('utf-8'),
            "iv": base64.b64encode(client_iv).decode('utf-8'),
            "tag": base64.b64encode(new_tag).decode('utf-8')
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )

@router.get("/users", response_model=List[UserBasicResponse])
async def get_users_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all users with 'user' role, excluding the current user.
    Only returns basic info (id and name)
    """
    users = db.query(User).filter(
        User.role == "user",
        User.id != current_user.id  # Exclude current user
    ).all()
    
    return [
        {
            "id": user.id,
            "name": user.full_name
        }
        for user in users
    ]

@router.post("/share")
async def share_file(
    request: ShareFileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    print(request.model_dump())
    # Validate permission type
    if request.permission not in [SharePermission.VIEW, SharePermission.DOWNLOAD]:
        raise HTTPException(status_code=400, detail="Invalid permission type")

    # Check if file exists and belongs to current user
    file = db.query(FileModel).filter(FileModel.id == request.file_id).first()
    if not file or file.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if user exists
    shared_user = db.query(User).filter(User.id == request.user_id).first()
    if not shared_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create share record
    share = FileShare(
        file_id=request.file_id,
        shared_with_user_id=request.user_id,
        share_link=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(seconds=request.expires_in_seconds),
        permission=request.permission
    )
    
    db.add(share)
    db.commit()
    db.refresh(share)
    
    # Generate the full share URL
    share_url = f"{settings.FRONTEND_URL}/file/{share.share_link}/{request.permission}"

    # Send email to the shared user
    await send_share_email(
        email=shared_user.email,
        file_name=file.filename,
        share_link=share_url,
        current_user=current_user
    )   
    
    return {
        "message": "File shared successfully",
        "share_link": share_url,
        "expires_at": share.expires_at,
        "permission": share.permission.value
    }


@router.get("/shared/{share_link}")
async def access_shared_file(
    share_link: str,
    db: Session = Depends(get_db)
):
    # Get share record
    share = db.query(FileShare).filter(FileShare.share_link == share_link).first()
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found")
    
    # Check if share link has expired
    if share.expires_at < datetime.utcnow():
        # Delete expired share
        db.delete(share)
        db.commit()
        raise HTTPException(status_code=410, detail="Share link has expired")
    
    # Get file
    file = db.query(FileModel).filter(FileModel.id == share.file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Read the encrypted file
        with open(file.file_path, "rb") as f:
            nonce = f.read(16)
            tag = f.read(16)
            encrypted_data = f.read()
        
        # Create cipher for decryption
        cipher = AES.new(SERVER_AES_KEY, AES.MODE_GCM, nonce=nonce)
        
        # Decrypt the data
        decrypted_data = cipher.decrypt_and_verify(encrypted_data, tag)

        # provide decrypted data as a response
        return {
            "filename": file.filename,
            "decrypted_data": base64.b64encode(decrypted_data).decode("utf-8"),
            "permission": share.permission.value,
            "file_type": file.file_type,
            "id": file.id
        }
        
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"Error accessing file: {str(e)}"
        )