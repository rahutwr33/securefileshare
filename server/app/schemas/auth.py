from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserInResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInResponse

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class InitialLoginResponse(BaseModel):
    message: str
    verification_id: str

class VerifyLoginRequest(BaseModel):
    verification_id: str
    code: str

class LoginResponse(Token):
    user: UserInResponse

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInResponse

class MFAVerifyRequest(BaseModel):
    verification_id: str
    code: str

class MFAResponse(BaseModel):
    message: str
    verification_id: str

class MFASetupResponse(BaseModel):
    """Response model for Email MFA setup"""
    message: str
    verification_id: str
    email: EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    full_name: str
    is_active: bool
    is_mfa_enabled: bool

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
