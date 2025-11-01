import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ENUM

# from app.books.models import BookModel

from app.db.base import Base
from app.shared.utils import UserRole


# if TYPE_CHECKING:
#     from app.books.models import BookModel




class UserModel(Base):
    __tablename__ = 'users'

    uid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
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
        nullable=False,
        default=UserRole.USER,
        server_default='user'
    )
    # books: Mapped[List["BookModel"]] = relationship(back_populates="user",
    #     cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
