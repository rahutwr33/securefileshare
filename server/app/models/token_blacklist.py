from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from ..database import Base

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    token = Column(String, primary_key=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now()) 