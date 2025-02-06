from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime
from enum import Enum
from app.models.user import UserRole

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserBase(BaseModel):
    email: EmailStr
    full_name: constr(min_length=1, max_length=100)

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    
    class Config:
        orm_mode = True

class UserBasicResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
