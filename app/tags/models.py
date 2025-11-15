import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
# To fix Circular import
if TYPE_CHECKING:
    from app.books.models import BookModel


# ---------- Association Table ----------
class BookTagModel(Base):
    __tablename__ = 'book_tags'

    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('books.bid'), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('tags.uid'), primary_key=True)


# ---------- Tag Model ----------
class TagModel(Base):
    __tablename__ = 'tags'

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    books: Mapped[List["BookModel"]] = relationship(
        secondary="book_tags",
        back_populates="tags",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Tag {self.name}>"

