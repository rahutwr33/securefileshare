from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Annotated
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User, UserRole
from ..models.file import File
from ..schemas.user import UserResponse
from ..schemas.auth import AdminLoginRequest, AdminLoginResponse, UserInResponse
from ..utils.auth import (
    verify_password, 
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..dependencies.auth import check_role

router = APIRouter(tags=["Admin"])

# Create admin dependency locally
get_admin_user = check_role([UserRole.ADMIN])
# Protected admin endpoints
@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all non-admin users",
    description="Get a list of all registered non-admin users. Only accessible by admins.",
    response_description="List of non-admin users retrieved successfully",
    dependencies=[Depends(get_admin_user)]
)
async def get_all_users(
    db: Session = Depends(get_db)
):
    # Query all users except those with ADMIN role
    return db.query(User).filter(User.role != UserRole.ADMIN).all()

@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Delete a user by their ID. Only accessible by admins.",
    dependencies=[Depends(get_admin_user)]
)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting admin users
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin users"
        )
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    return None

@router.delete(
    "/file/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a file",
    description="Delete a file by its ID. Only accessible by admins.",
    dependencies=[Depends(get_admin_user)]
)
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    # Find the file
    file = db.query(File).filter(File.id == file_id).first()
    
    # Check if file exists
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Delete the file
    db.delete(file)
    db.commit()
    
    return None


    


