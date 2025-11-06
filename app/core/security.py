import uuid
from datetime import timedelta
from typing import Optional, Dict, Any

from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
# from itsdangerous import URLSafeTimedSerializer

from app.core.config import settings
from app.core.logger import logger
from app.shared.utils import now_utc_dt

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


def create_jwt_token(user_data: dict, *, expires_delta: Optional[timedelta] = None, refresh: bool = False) -> str:
    """ Create JWT Access or Refresh Token.
        - Includes standard claims (exp, iat, jti, sub)
        - Supports custom expiry and refresh flag
    """
    current_time = now_utc_dt()

    # Default expiry times
    if expires_delta:
        expire = current_time + expires_delta
    else:
        expire = current_time + (
            settings.refresh_token_expiry if refresh
            else settings.access_token_expiry
        )

    payload = {
        "exp": expire,
        "iat": current_time,
        "nbf": current_time,
        "jti": str(uuid.uuid4()),  # unique token identifier (for revocation)
        "sub": str(user_data["uid"]), # subject = user id
        "refresh": refresh,
        "user": {
            "uid": str(user_data["uid"]),
            "email": user_data["email"],
            "role": user_data["role"]
        },
    }

    if settings.JWT_ISSUER:
        payload["iss"] = settings.JWT_ISSUER

    if settings.JWT_AUDIENCE:
        payload["aud"] = settings.JWT_AUDIENCE

    # Encode JWT
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    Returns the decoded payload if valid, else None.
    """

    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={"verify_exp": False}
        )
        return payload

    except ExpiredSignatureError:
        logger.warning("Token expired")
        return None

    except JWTError as e:
        logger.exception(f"{e}, Invalid JWT token")
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