from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

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


    async def check_user_exists(self, user_email: EmailStr) -> bool:
        user = await self.get_user_by_email(user_email)
        return True if user is not None else False


    async def create_user(self, user_data: UserCreate) -> UserModel:
        existing_user = await self.check_user_exists(user_data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        user = user_data.model_dump()  # Convert Pydantic model → dict
        user.pop("password")  # remove raw password
        new_user = UserModel(
            **user,
            hashed_password = user_data.password
        )

        self.db.add(new_user)

        try:
            await self.db.commit()
            await self.db.refresh(new_user)
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists (DB constraint)"
            )
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








