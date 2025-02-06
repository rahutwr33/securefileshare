from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime
from ..database import Base

class SharePermission(str, PyEnum):
    VIEW = "view"
    DOWNLOAD = "download"

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    stored_filename = Column(String)
    file_path = Column(String)
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)
    file_type = Column(String)
    # Relationships
    owner = relationship("User", back_populates="files")
    shares = relationship("FileShare", back_populates="file", cascade="all, delete-orphan")
