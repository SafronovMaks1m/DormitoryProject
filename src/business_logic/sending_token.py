from sqlalchemy.ext.asyncio import AsyncSession
from src.models.password_setup_token import PasswordSetupToken
from src.models.users import Users
from datetime import datetime, timezone, timedelta
from src.config import APPLICATION_PASSWORD_GMAIL
from email.message import EmailMessage
import smtplib
import secrets, hashlib

class SendToken:
    context = {
        "setup": {
            "https://localhost/users/setup-password?token=": "Your password setting link"       
        }
    }
    
    @classmethod
    def creating_token_instance(cls, user: Users) -> dict:
        token = secrets.token_urlsafe(32)
        hashed = hashlib.sha256(token.encode()).hexdigest()
        time = datetime.now(timezone.utc) + timedelta(days=20)
        db_passwod_token = PasswordSetupToken(
            hash_token = hashed,
            expires_at = time,
            user_id = user.id
        )
        return {"instance": db_passwod_token, "token": token}
    
    @classmethod
    def send_token_email(cls, email: str, token: str):
        msg = EmailMessage()
        msg["From"] = "safranov01@gmail.com"
        msg["To"] = email
        url, text = next(iter(cls.context["setup"].items()))
        msg["Subject"] = text
        msg.set_content(f"{url}{token}")
        
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login("safranov01@gmail.com", APPLICATION_PASSWORD_GMAIL)
            smtp.send_message(msg)