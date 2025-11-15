import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy import String, Integer, ForeignKey, func

from src.db.base import Base
from src.shared.utils import now_utc_dt

if TYPE_CHECKING:
    from src.user.models import UserModel
    from src.books.models import BookModel


# ---------- Review Model ----------
class ReviewModel(Base):
    __tablename__ = 'reviews'

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    book_uid: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.bid", ondelete="SET NULL"), nullable=True
    )
    user_uid: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.uid", ondelete="SET NULL"), nullable=True
    )
    review_text: Mapped[Optional[str]] = mapped_column(String, nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),
        nullable=False, default=now_utc_dt()
    )
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True),nullable=False,
        default=now_utc_dt(), onupdate=now_utc_dt()
    )
    # Relationships
    user: Mapped[Optional["UserModel"]] = relationship(
        back_populates="reviews",lazy="selectin")
    book: Mapped[Optional["BookModel"]] = relationship(
        back_populates="reviews",lazy="selectin")

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"