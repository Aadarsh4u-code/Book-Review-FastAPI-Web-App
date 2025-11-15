from typing import Annotated, TypeAlias
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.dependencies import get_book_service
from app.books.service import BookService
from app.db.session import get_db_session
from app.tags.services import TagService


async def get_tag_service(
        db_session: AsyncSession = Depends(get_db_session),
        book_service: BookService = Depends(get_book_service)
) -> TagService:
    return TagService(db_session, book_service)


TagServiceDep: TypeAlias = Annotated[TagService, Depends(get_tag_service)]