import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class TagCreate(BaseModel):
    name: str

class TagAdd(BaseModel):
    tags: List[TagCreate]

class TagResponse(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)