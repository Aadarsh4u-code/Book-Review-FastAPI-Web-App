from typing import Annotated, TypeAlias

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.books.service import BookService
from app.db.session import get_db_session


async def get_book_service(db_session: AsyncSession = Depends(get_db_session)):
    """ Dependency that provides a BookService instance.
        - db: injected async session
        - returns: BookService instance for use in routes
    """
    return BookService(db_session)


BookServiceDep: TypeAlias = Annotated[BookService, Depends(get_book_service)]
