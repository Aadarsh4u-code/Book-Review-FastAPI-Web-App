import uuid
from typing import Optional
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_hash_password, verify_password
from app.user.models import UserModel
from app.user.schemas import UserCreate, UserUpdate, UserDelete


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_user_by_email(self, user_email: EmailStr) -> Optional[UserModel]:
        result = await self.db.execute(select(UserModel).where(UserModel.email == user_email))
        user = result.scalar_one_or_none()
        if not user:
            return None
        return user


    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserModel]:
        result = await self.db.execute(
            select(UserModel).where(UserModel.uid == user_id)
        )
        return result.scalar_one_or_none()


    async def check_user_exists(self, user_email: EmailStr) -> bool:
        existing_user = await self.get_user_by_email(user_email)
        return True if existing_user is not None else False


    async def authenticate_user(self, email: EmailStr, password: str) -> Optional[UserModel]:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


    async def create_user(self, user_data: UserCreate) -> UserModel:
        user = user_data.model_dump()  # Convert Pydantic model → dict
        user.pop("password")  # remove raw password
        new_user = UserModel(
            **user,
            hashed_password = get_hash_password(user_data.password)
        )
        self.db.add(new_user)
        await self.db.flush()  # just flush (no commit needed)
        await self.db.refresh(new_user)
        return new_user

    async def update_user(self, user_data: UserUpdate) -> Optional[UserModel]:
        user = await self.get_user_by_email(user_data.email)
        if not user:
            return None

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UserDelete) -> bool | None:
        result = await self.db.execute(select(UserModel).where(UserModel.uid == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        await self.db.delete(user)
        await self.db.commit()
        return True








