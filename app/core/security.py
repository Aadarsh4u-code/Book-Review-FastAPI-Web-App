import uuid
from datetime import timedelta, datetime, timezone
from typing import Optional

from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
# from itsdangerous import URLSafeTimedSerializer

from app.core.config import setting
from app.core.logger import logger

###--- Constant Definition ---###
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# email_serializer = URLSafeTimedSerializer(
#     secret_key=setting.JWT_SECRET_KEY,
#     salt="email-verification"
# )


def get_hash_password(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def create_jwt_token(user_data: dict, expires_delta: Optional[timedelta] = None, refresh: bool = False) -> str:
    """ Create JWT Access or Refresh Token.
        - Includes standard claims (exp, iat, jti, sub)
        - Supports custom expiry and refresh flag
    """
    # Default expiry times
    if expires_delta is None:
        expires_delta = timedelta(days=setting.REFRESH_TOKEN_EXPIRY) if refresh else timedelta(
            minutes=setting.ACCESS_TOKEN_EXPIRY)

    # Current UTC time
    now_utc = datetime.now(timezone.utc)

    # Base payload
    payload = {
        "sub": str(user_data.get("id") or user_data.get("uid")), # subject = user id
        "refresh": refresh,
        "iat": int(now_utc.timestamp()),
        "exp": int((now_utc + expires_delta).timestamp()),
        "jti": str(uuid.uuid4()),  # unique token identifier (for revocation)
        "user": user_data,  # optional full user payload
    }

    # Encode JWT
    encoded_jwt = jwt.encode(payload, setting.JWT_SECRET_KEY, algorithm=setting.JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    Returns the decoded payload if valid, else None.
    """
    try:
        payload = jwt.decode(
            token,
            key=setting.JWT_SECRET_KEY,
            algorithms=[setting.JWT_ALGORITHM],
            options={"verify_exp": True}
        )

        # Check if token is expired manually (optional)
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            logger.warning("Token expired")
            return None

        return payload

    except ExpiredSignatureError:
        logger.warning("Token expired")
        return None

    except JWTError as e:
        logger.exception("Invalid JWT token")
        return None


# Create link
# def generate_email_token(email: str):
#     return email_serializer.dumps(email)


# Verify link
# def verify_email_token(token: str, max_age: int = settings.EMAIL_TOKEN_EXPIRY):
#     try:
#         email = email_serializer.loads(token, max_age=max_age)
#         return email
#     except Exception:
#         return None