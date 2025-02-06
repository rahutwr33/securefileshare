from sqlalchemy.orm import Session
from ..models.user import User, UserRole
from ..utils.auth import get_password_hash
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def init_admin(db: Session) -> None:
    """Initialize admin user if it doesn't exist"""
    try:
        # Check if any admin exists
        admin_count = db.query(User).filter(User.role == UserRole.ADMIN.value).count()
        if admin_count > 0:
            logger.info("Admin user already exists")
            return
        
        # Create admin user using environment variables
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")
        
        logger.info(f"Creating admin user with email: {admin_email}")
        
        if not all([admin_email, admin_password]):
            raise ValueError("Admin credentials not properly configured in environment")
        
        # Check if email already exists
        if db.query(User).filter(User.email == admin_email).first():
            raise ValueError(f"User with email {admin_email} already exists")
        
        admin_user = User(
            email=admin_email,
            full_name="System Administrator",
            hashed_password=get_password_hash(admin_password),
            role=UserRole.ADMIN.value,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        print("admin_user",admin_email, admin_password)
        logger.info("Admin user created successfully")
        
        # Verify admin was created
        created_admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
        if created_admin:
            logger.info(f"Verified admin creation. Email: {created_admin.email}, Role: {created_admin.role}")
            logger.info("Admin can login through the standard login endpoint")
        else:
            logger.error("Admin creation verification failed")
            
    except Exception as e:
        logger.error(f"Error initializing admin: {str(e)}")
        db.rollback()
        raise 