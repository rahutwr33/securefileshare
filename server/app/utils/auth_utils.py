from datetime import datetime
import re
import html
from email_validator import validate_email, EmailNotValidError
from typing import Dict, Any

def validate_password(password: str) -> bool:
    """
    Validate password strength
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def sanitize_input(data: str) -> str:
    """Sanitize string input to prevent XSS"""
    return html.escape(data.strip())

def validate_email_address(email: str) -> bool:
    """Validate email format and domain"""
    try:
        validation = validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError:
        return False

def validate_user_input(user_data: Dict[str, Any]) -> Dict[str, str]:
    """Validate and sanitize user input data"""
    errors = {}
    
    # Validate email
    if not validate_email_address(user_data.get("email", "")):
        errors["email"] = "Invalid email address"
    
    # Validate full_name
    full_name = user_data.get("full_name", "")
    if not full_name or len(full_name) < 2:
        errors["full_name"] = "Name must be at least 2 characters long"
    elif len(full_name) > 100:
        errors["full_name"] = "Name is too long"
    elif not re.match(r"^[a-zA-Z\s\-']+$", full_name):
        errors["full_name"] = "Name contains invalid characters"
    
    return errors 