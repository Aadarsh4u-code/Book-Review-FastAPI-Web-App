import os
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from itsdangerous import URLSafeTimedSerializer
from app.core.logger import logger

from app.core.config import settings



###################--------------------> Utility Schemas <-----------#######################

class UserRole(str, Enum):
    user = "user"
    manager = "manager"
    admin = "admin"
    superadmin = "superadmin"






###################--------------------> Pydantic Schemas <-----------#######################



###################--------------------> Utility Functions <-----------#######################

def now_utc_ts() -> int:
    """
        Get the current UTC time as a UNIX timestamp (integer seconds since epoch).
        Example: 1730812345
    """
    return int(datetime.now(timezone.utc).timestamp())


def now_utc_dt() -> datetime:
    """
        Get the current UTC time as a timezone-aware datetime object.
        Example: datetime(2025, 11, 5, 17, 25, 30, tzinfo=timezone.utc)
    """
    return datetime.now(timezone.utc)


###################--------------------> Itsdangerous Setup for Email Link<-----------#######################

email_token_serializer = URLSafeTimedSerializer(
        secret_key= settings.JWT_SECRET_KEY,
        salt= settings.EMAIL_SALT,
    )


def create_url_safe_token(data: dict) -> str:
    email_token = email_token_serializer.dumps(data)
    return email_token


def decode_url_safe_token(token: str):
    try:
        email_token = email_token_serializer.loads(token)
        return email_token
    except Exception as exc:
        logger.error(f"Failed to decode email url safe token: {exc}")




