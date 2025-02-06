import secrets
import time
from typing import Optional
from datetime import datetime, timedelta

def generate_share_link(
    resource_id: str,
    expiration_minutes: Optional[int] = 60,
    one_time: bool = True
) -> dict:
    """
    Generate a shareable link with expiration time.
    
    Args:
        resource_id (str): ID of the resource to be shared
        expiration_minutes (int, optional): Number of minutes until link expires. Defaults to 60.
        one_time (bool, optional): Whether the link can be used only once. Defaults to True.
    
    Returns:
        dict: Contains token, expiration timestamp, and other link details
    """
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    
    # Calculate expiration timestamp
    expiration_time = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    expiration_timestamp = int(expiration_time.timestamp())
    
    # Create share data
    share_data = {
        "token": token,
        "resource_id": resource_id,
        "expires_at": expiration_timestamp,
        "one_time": one_time,
        "created_at": int(time.time()),
        "is_valid": True
    }
    
    return share_data
