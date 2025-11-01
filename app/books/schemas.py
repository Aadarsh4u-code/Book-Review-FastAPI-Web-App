from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class BookBase(BaseModel):
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    publisher: str
    published_date: str
    page_count: int
    language: str
    rating: int = Field(gt=0, lt=6)

    model_config = ConfigDict(
        from_attributes=True,  # replaces orm_mode=True
        json_schema_extra={
            "example": {
                "title": "A new book",
                "author": "book writer name",
                "publisher": "The publisher",
                "published_date": "2020-01-01",
                "page_count": 150,
                "language": "en",
                "rating": 5,
            }
        }
    )


class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )

class BookRead(BookBase):
    bid: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
