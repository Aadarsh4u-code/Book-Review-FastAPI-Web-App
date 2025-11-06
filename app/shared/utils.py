from datetime import datetime, timezone
from enum import Enum







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