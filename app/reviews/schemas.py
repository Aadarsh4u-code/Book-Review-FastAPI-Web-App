import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------- Shared Base ----------
class ReviewBase(BaseModel):
    review_text: str = Field(..., min_length=2, max_length=50, description="Amazing book!")
    rating: float = Field(..., ge=1, le=5, description="Rating between 1 and 5")


class ReviewCreate(ReviewBase):
    pass


# ---------- Update ----------
class ReviewUpdate(ReviewBase):
    review_text: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


# ---------- Response ----------
class ReviewResponse(ReviewBase):
    uid: uuid.UUID
    book_uid: Optional[uuid.UUID]
    user_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True # Allows reading directly from ORM objects
    )