from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
import os

from ..database import get_db
from ..models.user import User
from ..models.token_blacklist import TokenBlacklist
from ..config import settings

# Security configurations
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Update the get_current_user function to check cookies
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get token from cookie
    auth_cookie = request.cookies.get("access_token")
    if not auth_cookie:
        raise credentials_exception
        
    # Remove quotes and 'Bearer ' prefix if present
    token = auth_cookie.strip('"')  # Remove surrounding quotes
    token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
    print("1111111",token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Add this function to check for blacklisted tokens
def is_token_blacklisted(db: Session, token: str) -> bool:
    """Check if a token is blacklisted"""
    return db.query(TokenBlacklist).filter(
        TokenBlacklist.token == token,
        TokenBlacklist.expires_at > datetime.utcnow()
    ).first() is not None

# Modify the existing verify_token function to check blacklist
async def verify_token(token: str, db: Session) -> Optional[str]:
    try:
        if is_token_blacklisted(db, token):
            return None
        
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
