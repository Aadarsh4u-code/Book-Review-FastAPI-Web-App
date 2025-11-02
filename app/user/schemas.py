import uuid
from datetime import datetime


from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.shared.utils import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=8)
    email: EmailStr
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    hashed_password: str = Field(..., exclude=True)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime
    role: UserRole = Field(default=UserRole.USER)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=8)
    email: EmailStr
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)

    model_config = ConfigDict(
        from_attributes = True,
        json_schema_extra= {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "johndoe123@co.com",
                "password": "testpass123",
            }
        }
    )


class UserUpdate(BaseModel):
    username: str = Field(..., min_length=1, max_length=8)
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    role: UserRole


class UserDelete(BaseModel):
    uid: uuid.UUID


class UserResponse(UserBase):
    uid: uuid.UUID




