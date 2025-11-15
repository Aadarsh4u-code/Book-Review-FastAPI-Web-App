from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from src.books.models import BookModel
from src.books.schemas import BookCreate, BookUpdate
from src.shared.exception_handlers import BookNotFound


class BookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_book(self, book_data: BookCreate, user_uid) -> BookModel:
        new_book = BookModel(**book_data.model_dump())
        new_book.user_uid = user_uid
        self.db.add(new_book)
        await self.db.refresh(new_book)
        return new_book

    async def get_book(self, book_id: uuid.UUID) -> Optional[BookModel]:
        result = await self.db.execute(
            select(BookModel).where(BookModel.bid == book_id))
        return result.scalar_one_or_none()

    async def update_book(self, book_id: uuid.UUID, book_data: BookUpdate) -> Optional[BookModel]:
        book = await self.get_book(book_id)
        if not book:
            raise BookNotFound(details={"book_id": str(book_id)})

        for field, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, field, value)
        await self.db.refresh(book)
        return book

    async def delete_book(self, book_id: uuid.UUID) -> bool:
        book = await self.get_book(book_id)
        if not book:
            raise BookNotFound(details={"book_id": str(book_id)})
        await self.db.delete(book)
        return True

    async def list_books(self) -> Sequence[BookModel]:
        results = await self.db.execute(select(BookModel))
        books = results.scalars().all()
        return books

    async def get_books_by_user(self, user_id: uuid.UUID) -> Sequence[BookModel]:
        results = await self.db.execute(select(BookModel).where(BookModel.user_uid == user_id))
        return results.scalars().all()
