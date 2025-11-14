from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, EmailStr

from app.books.schemas import BookBase
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
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    role: str
    books: List[BookBase]

    @classmethod
    def from_user(cls, user):
        return cls(
            uid=str(user.uid),
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            role=user.role.value,  # Convert enum to string
            books=user.books,
        )

class UserBasicDetails(BaseModel):
    uid: str
    email: EmailStr
    role: str

class TokenPayload(BaseModel):
    exp: int
    iat: int
    nbf: int
    jti: str
    sub: str
    refresh: bool
    user: UserBasicDetails


class EmailSchema(BaseModel):
    email_address: List[EmailStr]


class SignupResponse(BaseModel):
    message: str
    user: MeResponse
