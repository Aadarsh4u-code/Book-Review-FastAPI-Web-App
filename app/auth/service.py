from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.security import create_jwt_token, decode_jwt_token
from app.db.redis import redis_client
from app.shared.exception_handlers import InvalidToken, UserNotFound
from app.shared.utils import now_utc_dt, create_url_safe_token, decode_url_safe_token
from app.user.models import UserModel
from app.user.service import UserService
from app.worker.email_tasks import create_email_message, fastmail, render_verification_email_template, \
    render_verified_user_template


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

        user = await self.user_service.get_user_by_id(user_id)
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


    #  Send verification email after registration
    @staticmethod
    async def send_verification_email(user: UserModel):
        # Generate a short-lived verification token
        url_token = create_url_safe_token({"email": user.email})

        # Construct verification link
        verify_url = f"http://{settings.DOMAIN_URL}/api/v1/auth/verify_email/{url_token}"

        # Render HTML email body
        html_body = render_verification_email_template(user.username, verify_url)

        # Build and send message
        message = create_email_message(
            recipient=[user.email],
            subject="Verify your email address",
            body=html_body,
        )
        await fastmail.send_message(message)


    # Verify email when user clicks link
    async def verify_email_token(self, token: str):
        homepage_link = f"http://{settings.DOMAIN_URL}/api/v1/docs"

        payload = decode_url_safe_token(token)
        if not payload:
            raise InvalidToken(details=payload)

        user_email = payload.get("email")
        if user_email:
            user = await self.user_service.get_user_by_email(user_email)
            if not user:
                raise UserNotFound(details={"user_email": user_email})

            html_body = render_verified_user_template(homepage_link)
            if user.is_verified:
                return HTMLResponse(content=html_body)

            # Update user to verified
            await self.user_service.mark_user_verified(user.uid)
            return HTMLResponse(content=html_body)

        return JSONResponse(content={
            "message": "Error occurred during verification",
        }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)








