import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ENUM

from app.db.base import Base
from app.shared.utils import UserRole

# To fix Circular import
if TYPE_CHECKING:
    from app.books.models import BookModel
    from app.reviews.models import ReviewModel

# ---------- User Model ----------
class UserModel(Base):
    __tablename__ = 'users'

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())
    role: Mapped[UserRole] = mapped_column(
        ENUM(UserRole, name="user_role_enum", create_type=True),
        nullable=False, default=UserRole.user, server_default='user'
    )
    # Relationships
    books: Mapped[List["BookModel"]] = relationship(
        back_populates="user", lazy="selectin",
        cascade="save-update", passive_deletes=True
    )
    reviews: Mapped[List["ReviewModel"]] = relationship(
        back_populates="user", lazy="selectin",
        cascade="save-update", passive_deletes=True
    )

    def __repr__(self):
        return f"<User(id={self.uid}, email={self.email}, role={self.role})>"


