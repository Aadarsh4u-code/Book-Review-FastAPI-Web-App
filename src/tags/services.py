import uuid
from typing import List
from typing import Optional, Sequence
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.models import BookModel
from src.books.service import BookService
from src.shared.exception_handlers import BookNotFound, TagNotFound, TagAlreadyExists
from src.tags.models import TagModel
from src.tags.schemas import TagResponse, TagAdd, TagCreate
from src.user.schemas import UserID


class TagService:
    def __init__(self, db_session: AsyncSession, book_service: BookService):
        self.db = db_session
        self.book_service = book_service

    async def list_tags(self) -> Sequence[TagModel]:
        """Get all tags"""
        stmt = select(TagModel).order_by(TagModel.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_tag(self, tag_id: uuid.UUID) -> Optional[TagModel]:
        """Get a tag by id"""
        stmt = select(TagModel).where(TagModel.uid == tag_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_tag(self, tag_data: TagCreate) -> TagModel:
        """Create a new tag"""
        stmt = select(TagModel).where(TagModel.name == tag_data.name)
        result = await self.db.execute(stmt)
        existing_tag = result.scalars().first()
        if existing_tag:
            raise TagAlreadyExists(details={"name": existing_tag.name})
        new_tag = TagModel(name=tag_data.name)
        self.db.add(new_tag)
        await self.db.flush()
        await self.db.refresh(new_tag)
        return new_tag

    async def update_tag(self, tag_uid: uuid.UUID, tag_data: TagCreate) -> TagModel:
        """Update a tag"""
        tag = await self.get_tag(tag_uid)
        if not tag:
            raise TagNotFound(details={"tag_uid": tag_uid})

        for key, value in tag_data.model_dump().items():
            setattr(tag, key, value)

        await self.db.flush()
        await self.db.refresh(tag)
        return tag

    async def delete_tag(self, tag_uid: uuid.UUID) -> bool:
        """Delete a tag"""
        tag = await self.get_tag(tag_uid)
        if not tag:
            raise TagNotFound(details={"tag_uid": tag_uid})

        await self.db.delete(tag)
        return True

    async def add_tag_to_book(self, book_id: uuid.UUID, tag_data: TagAdd) -> BookModel:
        """Add tags to a book"""
        # Fetch book
        book = await self.book_service.get_book(book_id)
        if not book:
            raise BookNotFound(details={"book_id": book_id})

        # Process tag list
        for tag_item in tag_data.tags:
            stmt = select(TagModel).where(TagModel.name == tag_item.name)
            tag_result = await self.db.execute(stmt)
            tag = tag_result.scalars().first()
            if not tag:
                # If not tag is create one and assign but the problem is typo error with tags
                # tag = TagModel(name=tag_item.name)
                # self.db.add(tag)
                # await self.db.flush()
                # await self.db.refresh(tag)
                raise TagNotFound(details={"tag_name": tag_item.name})

            book.tags.append(tag) # This line updates the relationship table (usually BookTagModel).

        await self.db.flush()
        await self.db.refresh(book)
        return book

