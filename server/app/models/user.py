from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ..database import Base

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    files = relationship("File", back_populates="owner")
    # Files shared with this user
    shared_files = relationship("FileShare", back_populates="shared_with_user")

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def is_user(self) -> bool:
        return self.role == UserRole.USER

    def is_guest(self) -> bool:
        return self.role == "guest"
