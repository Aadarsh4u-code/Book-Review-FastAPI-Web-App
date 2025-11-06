from typing import TypeAlias, Annotated, Optional, List, Any

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from app.core.security import decode_jwt_token
from app.db.redis import redis_client
from app.db.session import get_db_session
from app.shared.utils import UserRole
from app.user.dependencies import get_user_service, UserServiceDep
from app.user.models import UserModel
from app.user.service import UserService


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, token_type: str = "access"):
        super().__init__(auto_error=auto_error)
        self.token_type = token_type

    async def __call__(self, request: Request) -> dict[str, Any]:
        # credentials comes from HTTPBearer automatically
        credentials = await super().__call__(request)
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing credentials")

        token = credentials.credentials

        if token.count('.') != 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token format. Expected 3 segments, got {token.count('.') + 1}"
            )

        # Check if token is empty or malformed
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty token provided"
            )



        # Decode token
        payload = decode_jwt_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        # Check revocation - for access tokens, check regular revoked list
        # For refresh tokens, check user-specific revoked list
        jti = payload.get("jti")
        if jti:
            if payload.get("refresh"):
                # For refresh tokens, check user-specific revocation
                user_id = payload.get("user", {}).get("uid")
                if user_id:
                    user_refresh_key = f"revoked:user_refresh_tokens:{user_id}:{jti}"
                    if await redis_client.is_token_revoked(user_refresh_key):
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token revoked"
                        )
            else:
                # For access tokens, check regular revocation
                if await redis_client.is_token_revoked(jti):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token revoked"
                    )

        # Verify token type (access or refresh)
        await self.verify_token_data(payload)
        return payload

    async def verify_token_data(self, payload: dict):
        NotImplementedError("This method is not implemented please override this method in subclass.")


class AccessTokenBearer(TokenBearer):
    async def verify_token_data(self, payload: dict):
        if payload.get("refresh", False):  # Reject if it's a refresh token
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token required"
            )


class RefreshTokenBearer(TokenBearer):
    async def verify_token_data(self, payload: dict):
        if not payload.get("refresh", False): # Reject if it's NOT a refresh token
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required"
            )



#################--------Dependencies-----------########################
# Export dependencies
AccessTokenDep = Depends(AccessTokenBearer())
RefreshTokenDep = Depends(RefreshTokenBearer())


async def get_auth_service(
        db_session: AsyncSession = Depends(get_db_session),
        user_service: UserService = Depends(get_user_service)):
    return AuthService(db_session, user_service)

AuthServiceDep: TypeAlias = Annotated[AuthService, Depends(get_auth_service)]



# Get Current User and Its Detail
async def get_current_user(user_service: UserServiceDep,
        token_payload: dict = AccessTokenDep
        ) -> Optional[UserModel]:
    user_data = token_payload.get("user")
    if not user_data or "email" not in user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = await user_service.get_user_by_email(user_data["email"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: UserModel = Depends(get_current_user)) -> bool:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role.value}' not allowed. Requires one of: {self.allowed_roles}",
            )
        return True

def get_role_checker_dep(allowed_roles: list[UserRole]):
    return Depends(RoleChecker(allowed_roles))
