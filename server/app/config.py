from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET_KEY: str = "your-very-long-and-very-random-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File storage settings
    UPLOAD_DIR: str = "uploads"

    # Email settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "rt29507@gmail.com"
    SMTP_PASSWORD: str = "qglq yjjn cppr snem"
    MAIL_TLS: bool = False
    MAIL_SSL: bool = True

    # Frontend settings
    FRONTEND_URL: str = "http://localhost:3000"

    # Admin settings
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "Admin@123!"

    SERVER_AES_KEY: str
    SERVER_AES_IV: str

    BASE_URL: str = "http://127.0.0.1:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 