from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
from enum import Enum

class SharePermission(str, Enum):
    VIEW = "view"
    DOWNLOAD = "download"

class ShareRequest(BaseModel):
    permission: SharePermission
    expiry_hours: Optional[int] = 24  # Default 24 hours

class ShareResponse(BaseModel):
    share_link: str
    expiry_date: datetime
    permission: SharePermission

class FileBase(BaseModel):
    filename: str

class FileCreate(FileBase):
    pass

class FileResponse(BaseModel):
    id: int
    filename: str
    size: int
    upload_date: datetime

class FileUploadResponse(BaseModel):
    id: int
    filename: str
    size: int
    upload_date: datetime

class FileShareRequest(BaseModel):
    expires_in_days: Optional[int] = 7
    can_download: Optional[bool] = False
    
    @validator('expires_in_days')
    def validate_expiry(cls, v):
        if v < 1 or v > 30:
            raise ValueError('Expiry must be between 1 and 30 days')
        return v

class FileShareResponse(BaseModel):
    share_link: str
    expires_at: datetime
    can_download: bool

class ShareFileRequest(BaseModel):
    file_id: int
    user_id: int
    expires_in_seconds: int  # Default 15 minutes
    permission: str
