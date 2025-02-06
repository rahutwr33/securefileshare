from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from .file import SharePermission

class FileShare(Base):
    __tablename__ = "file_shares"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    shared_with_user_id = Column(Integer, ForeignKey("users.id"))
    share_link = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    permission = Column(Enum(SharePermission))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    file = relationship("File", back_populates="shares")
    shared_with_user = relationship("User", back_populates="shared_files") 
    
    