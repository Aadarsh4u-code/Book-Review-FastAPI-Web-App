from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_jwt_token, decode_jwt_token
from app.db.redis import redis_client
from app.shared.utils import now_utc_dt
from app.user.service import UserService


class AuthService:
    def __init__(self, db: AsyncSession, user_service: UserService):
        self.db = db
        self.user_service = user_service


    async def login(self, email: EmailStr, password: str) -> Dict[str, Any]:
        user = await self.user_service.authenticate_user(email, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account deactivated"
            )
        user_data = {"uid": user.uid, "email": user.email, "role": user.role.value}

        access_token = create_jwt_token(user_data, refresh=False)
        refresh_token = create_jwt_token(user_data, refresh=True)

        # Store the refresh token mapping
        refresh_payload = decode_jwt_token(refresh_token)
        if refresh_payload and refresh_payload.get("jti"):
            await redis_client.store_refresh_token(
                user.uid,
                refresh_payload['jti'],
                refresh_payload.get("exp")
            )
            print(f"Stored refresh token {refresh_payload['jti']} for user {user.uid}")

        return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }


    async def refresh(self, token_payload: Dict[str, Any]) -> Dict[str, Any]:
        # Verify it's a refresh token
        if not token_payload.get("refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Check if token is expired (additional safety check)
        exp_timestamp = token_payload.get("exp")
        if exp_timestamp and datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) < now_utc_dt():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired token"
            )

        user_data = token_payload.get("user", {})
        user_id = user_data.get("uid")
        jti = token_payload.get("jti")

        if await redis_client.is_token_revoked(jti):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")

        user = await self.user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")

        # Revoke old refresh
        await redis_client.add_to_blocklist(jti, exp_timestamp)

        # New tokens
        new_access_token = create_jwt_token(user_data, refresh=False)
        new_refresh_token = create_jwt_token(user_data, refresh=True)
        new_payload = decode_jwt_token(new_refresh_token)
        await redis_client.store_refresh_token(user_id, new_payload["jti"], new_payload["exp"])

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def logout(access_payload: dict):
        user_id = access_payload["user"]["uid"]
        jti = access_payload["jti"]
        exp = access_payload["exp"]

        await redis_client.add_to_blocklist(jti, exp)
        await redis_client.revoke_user_refresh_tokens(user_id)
        return {"message": "Successfully logged out"}


    @staticmethod
    async def revoke_all(access_payload: dict):
        """Manually revoke all refresh tokens (admin/self logout everywhere)"""
        user_id = access_payload["user"]["uid"]
        await redis_client.revoke_user_refresh_tokens(user_id)
        return {"message": "All refresh tokens revoked"}
