from typing import TypeAlias, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.user.service import UserService


async def get_user_service(db_session: AsyncSession = Depends(get_session)):
    return UserService(db_session)


user_service_dep: TypeAlias = Annotated[UserService, Depends(get_user_service)]
