from typing import TypeAlias, Annotated

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import TokenPayload
from app.auth.service import AuthService
from app.core.security import decode_jwt_token
from app.db.redis import redis_client
from app.db.session import get_db_session
from app.user.dependencies import get_user_service
from app.user.service import UserService


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, token_type: str = "access"):
        super().__init__(auto_error=auto_error)
        self.token_type = token_type

    async def __call__(self, request: Request) -> TokenPayload:
        # credentials comes from HTTPBearer automatically
        credentials = await super().__call__(request)
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing credentials")

        token = credentials.credentials

        # Check if token is empty or malformed
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty token provided"
            )

        if token.count('.') != 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token format. Expected 3 segments, got {token.count('.') + 1}"
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
        return TokenPayload(**payload)

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


# Higher Order Function
def role_checker_factory(allowed_roles: list[str]):
    """
    Returns a dependency function that checks if the current user's role is in allowed_roles.
    """

    async def role_checker(token_payload: TokenPayload = AccessTokenDep):
        user_role = token_payload.user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return token_payload

    return role_checker
