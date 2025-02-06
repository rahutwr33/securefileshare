from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from collections import defaultdict

from ..models.user import User, UserRole
from ..models.verification import LoginVerification
from ..models.token_blacklist import TokenBlacklist
from ..utils.auth import get_password_hash, verify_password
from ..utils.auth_utils import validate_password, sanitize_input, validate_user_input
from ..config import settings

# Rate limiting storage
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 100
LOGIN_TIMEOUT_MINUTES = 15

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: dict) -> User:
        """Handle user registration logic"""
        validation_errors = validate_user_input(user_data)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation_errors
            )
        
        sanitized_full_name = sanitize_input(user_data["full_name"])
        
        if self.db.query(User).filter(User.email == user_data["email"].lower()).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if not validate_password(user_data["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain uppercase, lowercase, number and special character"
            )
        
        hashed_password = get_password_hash(user_data["password"])
        db_user = User(
            email=user_data["email"].lower(),
            full_name=sanitized_full_name,
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create user"
            )

    def check_login_attempts(self, client_ip: str):
        """Handle rate limiting logic"""
        current_time = datetime.utcnow()
        
        login_attempts[client_ip] = [
            attempt_time for attempt_time in login_attempts[client_ip]
            if current_time - attempt_time < timedelta(minutes=LOGIN_TIMEOUT_MINUTES)
        ]
        
        if len(login_attempts[client_ip]) >= MAX_LOGIN_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Please try again in {LOGIN_TIMEOUT_MINUTES} minutes"
            )
        
        login_attempts[client_ip].append(current_time)

    def blacklist_token(self, token: str) -> bool:
        """Remove token from database on logout"""
        try:
            # Find and delete the token
            result = self.db.query(TokenBlacklist).filter(
                TokenBlacklist.token == token
            ).delete()
            
            self.db.commit()
            return result > 0  # Returns True if a token was deleted
            
        except Exception:
            self.db.rollback()
            return False 