from typing import Optional, Literal
from pydantic import BaseModel, EmailStr

from app.shared.utils import UserRole


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.user


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: Literal["bearer"] = "bearer"


class MeResponse(BaseModel):
    uid: str
    email: EmailStr
    role: str

    @classmethod
    def from_user(cls, user):
        return cls(
            uid=str(user.uid),
            email=user.email,
            role=user.role.value
        )


class TokenPayload(BaseModel):
    exp: int
    iat: int
    nbf: int
    jti: str
    sub: str
    refresh: bool
    user: dict




