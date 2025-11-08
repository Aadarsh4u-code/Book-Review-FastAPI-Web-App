import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, EmailStr


###################--------------------> Utility Schemas <-----------#######################

class UserRole(str, Enum):
    user = "user"
    manager = "manager"
    admin = "admin"
    superadmin = "superadmin"

class EnvironmentSchema(str, Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"




###################--------------------> Pydantic Schemas <-----------#######################

class UIDSchema(BaseModel):
    uid: uuid.UUID = Field(..., description="Unique identifier")

    model_config = ConfigDict(
        # for nicer OpenAPI docs and JSON serialization
        json_schema_extra={
            "example": {"uid": "c5b89b48-372a-4b57-9b7f-1d935dfec45f"}
        }
    )

class EmailSchema(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")

    model_config = ConfigDict(
        # for nicer OpenAPI docs and JSON serialization
        json_schema_extra={
            "example": {"email": "aadarsh@example.com"}
        }
    )





###################--------------------> Utility Functions <-----------#######################

def now_utc_ts() -> int:
    """
        Get the current UTC time as a UNIX timestamp (integer seconds since epoch).
        Example: 1730812345
    """
    return int(datetime.now(timezone.utc).timestamp())


def now_utc_dt() -> datetime:
    """
        Get the current UTC time as a timezone-aware datetime object.
        Example: datetime(2025, 11, 5, 17, 25, 30, tzinfo=timezone.utc)
    """
    return datetime.now(timezone.utc)