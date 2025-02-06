from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from dotenv import load_dotenv
from pathlib import Path
from app.models.user import User
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD"),
    MAIL_FROM=os.getenv("SMTP_USER"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", 465)),
    MAIL_SERVER=os.getenv("SMTP_HOST"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'email-templates'
)

fastmail = FastMail(conf)

async def send_verification_email(email: str, code: str, verification_link: str):
    try:
        message = MessageSchema(
            subject="Login Verification Code",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <p>Your verification code is: <strong>{code}</strong></p>
                    <strong>This code will expire in 10 minutes.</strong>
                </body>
            </html>
            """,
            subtype="html"
        )
        
        await fastmail.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False 

async def send_share_email(email: str, file_name: str, share_link: str, current_user: User):
    try:
        print(f"Sending share email to {email} for file {file_name} shared by {current_user.full_name} with link {share_link}")
        message = MessageSchema(
            subject="File Shared with You",
            recipients=[email],
            body=f"""
            <html>
                <body>
                    <p>You have been invited to view the file <strong>{file_name}</strong> shared by <strong>{current_user.full_name}</strong>. Click the link below to access the file: <a href="{share_link}">{share_link}</a></p>
                </body>
            </html>
            """,
            subtype="html"
        )
        
        await fastmail.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
