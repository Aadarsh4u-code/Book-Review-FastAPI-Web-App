import os
from datetime import datetime
from typing import List, Sequence, Union

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

def create_email_message(recipient: Sequence[Union[str, EmailStr]], subject: str, body: str):
    name_email_list = [NameEmail(name="", email=str(email)) for email in recipient]
    message = MessageSchema(
        recipients=name_email_list,
        subject=subject,
        body=body,
        subtype=MessageType.html
    )
    return message


###################--------------------> Generate Emails Templates<-----------#######################
def render_verification_email_template(user_name: str, verification_link: str) -> str:
    # Get absolute path to this file’s directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up one level (from shared → app) and into templates
    template_path = os.path.join(base_dir, "..", "templates", "verify_email.html")

    # Normalize path
    template_path = os.path.normpath(template_path)

    # Read file
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

        # Optionally replace placeholders
        html_content = html_content.replace("{{user_name}}", user_name)
        html_content = html_content.replace("{{verification_link}}", verification_link)
        html_content = html_content.replace("{{year}}", str(datetime.now().year))

        return html_content



def render_verified_user_template(homepage_link: str) -> str:
    # Get absolute path to this file’s directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up one level (from shared → app) and into templates
    template_path = os.path.join(base_dir, "..", "templates", "account_verified.html")

    # Normalize path
    template_path = os.path.normpath(template_path)

    # Read file
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

        # Optionally replace placeholders
        html_content = html_content.replace("{{homepage_link}}", homepage_link)
        html_content = html_content.replace("{{year}}", str(datetime.now().year))

        return html_content
