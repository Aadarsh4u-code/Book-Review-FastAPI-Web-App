import uuid
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy import String, Integer, ForeignKey

from app.db.base import Base

if TYPE_CHECKING:
    from app.user.models import UserModel
    from app.reviews.models import ReviewModel


# ---------- Book Model ----------
class BookModel(Base):
    __tablename__ = "books"

    bid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    publisher: Mapped[str] = mapped_column(String, nullable=False)
    published_date: Mapped[str] = mapped_column(String, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    user_uid: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.uid", ondelete="SET NULL"), nullable=True)

    # Relationships
    user: Mapped[Optional["UserModel"]] = relationship(
        back_populates="books",
        lazy="selectin"
    )
    reviews: Mapped[List["ReviewModel"]] = relationship(  # type: ignore[type-arg]
        back_populates="book", lazy="selectin"
    )

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"





