from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from ..database import Base

class LoginVerification(Base):
    __tablename__ = "login_verifications"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at 