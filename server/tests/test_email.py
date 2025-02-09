import pytest
from app.utils.email import send_verification_email, send_share_email
from unittest.mock import patch, MagicMock, AsyncMock
import aiosmtplib
from email.message import EmailMessage
from app.config import settings
import os
from app.models.user import User, UserRole

@pytest.mark.asyncio
async def test_send_verification_email():
    # Create mocks
    mock_smtp = AsyncMock()
    mock_message = EmailMessage()

    # Configure SMTP mock
    mock_smtp.__aenter__ = AsyncMock(return_value=mock_smtp)
    mock_smtp.__aexit__ = AsyncMock()
    mock_smtp.send_message = AsyncMock(return_value=True)

    # Set environment variables for email settings
    email_settings = {
        'SMTP_HOST': 'smtp.example.com',
        'SMTP_PORT': '587',
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password',
        'MAIL_FROM': 'test@example.com',
        'MAIL_FROM_NAME': 'Test Sender'
    }
    
    with patch.dict(os.environ, email_settings), \
         patch('aiosmtplib.SMTP', return_value=mock_smtp), \
         patch('email.message.EmailMessage', return_value=mock_message):
        
        try:
            result = await send_verification_email(
                email="test@example.com",
                code="123456",
                verification_link="http://example.com/verify"
            )
            print("Verification email sent successfully")
        except Exception as e:
            print(f"Error sending verification email: {str(e)}")
            raise
        
        # Verify email was sent
        assert mock_smtp.send_message.called
        assert result == True

@pytest.mark.asyncio
async def test_send_share_email():
    # Create mocks
    mock_smtp = AsyncMock()
    mock_message = EmailMessage()

    # Configure SMTP mock
    mock_smtp.__aenter__ = AsyncMock(return_value=mock_smtp)
    mock_smtp.__aexit__ = AsyncMock()
    mock_smtp.send_message = AsyncMock(return_value=True)

    # Create a test user
    test_user = User(
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER
    )

    # Set environment variables for email settings
    email_settings = {
        'SMTP_HOST': 'smtp.example.com',
        'SMTP_PORT': '587',
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password',
        'MAIL_FROM': 'test@example.com',
        'MAIL_FROM_NAME': 'Test Sender'
    }
    
    with patch.dict(os.environ, email_settings), \
         patch('aiosmtplib.SMTP', return_value=mock_smtp), \
         patch('email.message.EmailMessage', return_value=mock_message):
        
        try:
            result = await send_share_email(
                email="recipient@example.com",
                file_name="test.txt",
                share_link="http://example.com/share/abc123",
                current_user=test_user  # Pass actual User object
            )
            print("Share email sent successfully")
        except Exception as e:
            print(f"Error sending share email: {str(e)}")
            raise
        
        # Verify email was sent
        assert mock_smtp.send_message.called
        assert result == True 