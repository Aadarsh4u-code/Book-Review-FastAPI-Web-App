# Password hashing, token creation
from enum import Enum



class UserRole(str, Enum):
    user = "user"
    manager = "manager"
    admin = "admin"
    superadmin = "superadmin"
