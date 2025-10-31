from typing import  Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.books.models import Book
from app.books.schemas import BookCreate, BookUpdate


class BookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_book(self, book_data: BookCreate) -> Book:
        new_book = Book(**book_data.model_dump())
        self.db.add(new_book)
        await self.db.commit()
        await self.db.refresh(new_book)
        return new_book


    async def get_book(self, book_id: uuid.UUID) -> Optional[Book]:
        result = await self.db.execute(
            select(Book).where(Book.id == book_id))
        return result.scalar_one_or_none()


    async def update_book(self, book_id: uuid.UUID, book_data: BookUpdate) -> Optional[Book]:
        book = await self.get_book(book_id)
        if not book:
            return None

        for field, value in book_data.model_dump(exclude_unset=True).items():
            setattr(book, field, value)
        await self.db.commit()
        await self.db.refresh(book)
        return book


    async def delete_book(self, book_id: uuid.UUID) -> bool:
        book = await self.get_book(book_id)
        if not book:
            return False
        await self.db.delete(book)
        await self.db.commit()
        return True


    async def list_books(self)-> List[Book]:
        results = await self.db.execute(select(Book))
        return list(results.scalars().all())

