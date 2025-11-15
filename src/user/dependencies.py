from typing import TypeAlias, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db_session
from src.user.service import UserService


async def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> UserService:
    """
        FastAPI dependency that provides a UserService instance
        with a connected database session.
    """
    return UserService(db_session)


UserServiceDep: TypeAlias = Annotated[UserService, Depends(get_user_service)]
