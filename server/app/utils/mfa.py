from datetime import datetime, timedelta
import secrets
from ..utils.email import send_verification_email

class MFAHandler:
    @staticmethod
    def generate_code() -> str:
        """Generate a 6-digit verification code"""
        return ''.join(secrets.choice('0123456789') for _ in range(8))
    
    @staticmethod
    async def send_mfa_code(email: str, code: str) -> bool:
        """Send MFA code via email"""
        subject = "Your Login Verification Code"
        content = f"Your verification code is: {code}\nThis code will expire in 10 minutes."
        return await send_verification_email(email, code, None)
    
    @staticmethod
    def verify_code(stored_code: str, provided_code: str) -> bool:
        """Verify the provided code matches the stored code"""
        return stored_code == provided_code 