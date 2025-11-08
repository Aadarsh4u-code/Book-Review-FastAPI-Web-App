from typing import Annotated, TypeAlias
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.service import BookService
from app.db.session import get_db_session
from app.reviews.service import ReviewService
from app.user.service import UserService


async def get_book_service(db: AsyncSession = Depends(get_db_session)):
    return BookService(db)

async def get_user_service(db: AsyncSession = Depends(get_db_session)):
    return UserService(db)

async def get_review_service(
    db: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(get_user_service),
    book_service: BookService = Depends(get_book_service)
):
    return ReviewService(db, user_service, book_service)

ReviewServiceDep: TypeAlias = Annotated[ReviewService, Depends(get_review_service)]
