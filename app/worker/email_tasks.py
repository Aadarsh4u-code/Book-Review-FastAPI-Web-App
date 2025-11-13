from typing import List

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr, NameEmail

from app.core.config import settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

mail_config = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS = settings.MAIL_STARTTLS,
    MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
    USE_CREDENTIALS = settings.USE_CREDENTIALS,
    VALIDATE_CERTS = settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER= Path(BASE_DIR, "templates"),
)

fastmail = FastMail(config=mail_config)

def create_email_message(recipient: List[EmailStr], subject: str, body: str):
    name_email_list = [NameEmail(name="", email=str(email)) for email in recipient]
    message = MessageSchema(
        recipients=name_email_list,
        subject=subject,
        body=body,
        subtype=MessageType.html
    )
    return message
