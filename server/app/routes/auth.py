from fastapi import APIRouter, Depends, HTTPException, status, Body, Request, Response
from sqlalchemy.orm import Session
from typing import Optional, Annotated, Dict, Any
import re
from datetime import timedelta, datetime
import secrets
import string
import os
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from email_validator import validate_email, EmailNotValidError
import html
from collections import defaultdict

from ..database import get_db
from ..models.user import User, UserRole
from ..models.verification import LoginVerification
from ..schemas.user import UserCreate, UserResponse
from ..utils.auth import (
    get_password_hash, 
    create_access_token, 
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    get_current_active_user
)
from ..schemas.auth import (
    Token, 
    LoginRequest, 
    UserInResponse, 
    InitialLoginResponse,
    VerifyLoginRequest,
    MFASetupResponse,
    MFAVerifyRequest
)
from ..utils.email import send_verification_email
from ..dependencies.auth import check_role
from ..models.token_blacklist import TokenBlacklist
from ..config import settings
from ..services.auth_service import AuthService
from ..utils.auth_utils import validate_email_address
from ..utils.mfa import MFAHandler

router = APIRouter(tags=["Auth"])

# Create role-based dependencies locally
get_admin_user = check_role([UserRole.ADMIN])
get_any_user = check_role([UserRole.ADMIN, UserRole.USER])

# Add these near the top with other router definitions
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Add these variables at the top of the file with other constants
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT_MINUTES = 15

# Create an in-memory store for login attempts
login_attempts = defaultdict(list)

def validate_password(password: str) -> bool:
    """
    Validate password strength
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def sanitize_input(data: str) -> str:
    """Sanitize string input to prevent XSS"""
    return html.escape(data.strip())

def validate_email_address(email: str) -> bool:
    """Validate email format and domain"""
    try:
        validation = validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError:
        return False

def validate_user_input(user_data: Dict[str, Any]) -> Dict[str, str]:
    """Validate and sanitize user input data"""
    errors = {}
    
    # Validate email
    if not validate_email_address(user_data.get("email", "")):
        errors["email"] = "Invalid email address"
    
    # Validate full_name
    full_name = user_data.get("full_name", "")
    if not full_name or len(full_name) < 2:
        errors["full_name"] = "Name must be at least 2 characters long"
    elif len(full_name) > 100:
        errors["full_name"] = "Name is too long"
    elif not re.match(r"^[a-zA-Z\s\-']+$", full_name):
        errors["full_name"] = "Name contains invalid characters"
    
    return errors

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Register a new user with the system.
    
    The password must meet the following criteria:
    * At least 8 characters long
    * Contains at least one uppercase letter
    * Contains at least one lowercase letter
    * Contains at least one number
    * Contains at least one special character
    """,
    response_description="Successfully registered user"
)
async def register_user(
    user: Annotated[UserCreate, Body(
        example={
            "email": "user@example.com",
            "full_name": "John Doe",
            "password": "StrongPass123!"
        }
    )],
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.register_user(user.dict())

def generate_verification_code():
    # Generate a 6-digit code
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def generate_verification_id():
    return secrets.token_urlsafe(32)

@router.post(
    "/login",
    response_model=InitialLoginResponse,
    summary="Initiate user login",
    description="""
    Start the login process for any user (admin or regular user).
    
    This endpoint:
    1. Validates user credentials
    2. Sends a verification code via email
    3. Returns a verification ID for the next step
    """,
    response_description="Verification code sent successfully"
)
async def login(
    request: Request,
    login_data: Annotated[LoginRequest, Body(
        example={
            "email": "user@example.com",
            "password": "StrongPass123!"
        }
    )],
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    auth_service.check_login_attempts(request.client.host)
    
    if not validate_email_address(login_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    # Find user by email without role restriction
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Generate MFA code
    mfa_code = MFAHandler.generate_code()
    verification_id = secrets.token_urlsafe(32)
    
    # Store verification details
    verification = LoginVerification(
        id=verification_id,
        user_id=user.id,
        code=mfa_code,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(verification)
    db.commit()
    
    # Send MFA code via email
    email_sent = await MFAHandler.send_mfa_code(user.email, mfa_code)
    if not email_sent:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification code"
        )
    
    return InitialLoginResponse(
        message="Verification code sent to your email",
        verification_id=verification_id
    )

@router.post(
    "/verify-login",
    response_model=Token,
    summary="Complete login with verification",
    description="""
    Complete the login process by verifying the code sent via email.
    
    This endpoint:
    1. Validates the verification code
    2. Issues an access token upon successful verification
    3. Returns user details along with the token
    """,
    response_description="Login successful"
)
async def verify_login(
    verify_data: Annotated[VerifyLoginRequest, Body(
        example={
            "verification_id": "abc123",
            "code": "123456"
        }
    )],
    db: Session = Depends(get_db),
    response: Response = Response
):
    # Get verification record
    verification = db.query(LoginVerification).filter(
        LoginVerification.id == verify_data.verification_id,
        LoginVerification.is_used == False
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification ID"
        )
    
    # Check if verification is expired
    if verification.is_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired"
        )
    
    # Check if code matches
    if verification.code != verify_data.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Get user
    user = db.query(User).filter(User.id == verification.user_id).first()
    
    # Mark verification as used
    verification.is_used = True
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Store the token in the database
    try:
        expiresat = datetime.utcnow() + access_token_expires
        expiry_timestamp = expiresat.timestamp()
        expiry_timestamp_int = int(expiry_timestamp)

        token_record = TokenBlacklist(
            token=access_token,
            expires_at=expiresat
        )
        
        existing_token = db.query(TokenBlacklist).filter(
            TokenBlacklist.token == access_token
        ).first()
        
        if existing_token:
            db.delete(existing_token)
        
        db.add(token_record)
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store token: {str(e)}"
        )
    
    # Create response with user data
    user_response = UserInResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )

    # Set cookie only during verify-login
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=expiry_timestamp_int
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@router.post("/logout")
async def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_any_user)
):
    """Simplified logout that just removes the cookie"""
    response.delete_cookie(
        key="access_token",
        secure=True,
        httponly=True,
        samesite="lax"
    )
    return {"message": "Successfully logged out"}

@router.get("/profile", response_model=UserInResponse)
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get the profile details of the currently logged-in user.
    This is a protected route that requires authentication.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role
    }


    
