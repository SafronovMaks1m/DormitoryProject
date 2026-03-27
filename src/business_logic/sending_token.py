from sqlalchemy.ext.asyncio import AsyncSession
from src.models.password_setup_token import PasswordSetupToken
from src.models.users import Users
from datetime import datetime, timezone, timedelta
from src.config import APPLICATION_PASSWORD
from email.message import EmailMessage
import aiosmtplib
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
            user = user
        )
        return {"instance": db_passwod_token, "token": token}
    
    @classmethod
    async def send_token_email(cls, email: str, token: str):
        msg = EmailMessage()
        msg["From"] = "safranov01@gmail.com"
        msg["To"] = email
        url, text = next(iter(cls.context["setup"].items()))
        msg["Subject"] = text
        msg.set_content(f"{url}{token}")
        
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username="safranov01@gmail.com",
            password=APPLICATION_PASSWORD
        )