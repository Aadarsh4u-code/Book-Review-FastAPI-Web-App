from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, TypeAlias, Any, Optional

from pydantic import BaseModel
from sqlalchemy.sql.annotation import Annotated

from app.core.security import decode_jwt_token
from app.db.redis import token_in_blocklist


# from app.core.token_blocklist import is_token_revoked

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing credentials")

        token = credentials.credentials

        payload = decode_jwt_token(token)

        if not self.is_valid_token(token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail={"error": "JWT token is invalid or revoked.",
                                        "resolution": "Get new token."})

        if await token_in_blocklist(payload.get("jti")):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail={"error": "JWT token is invalid or revoked.",
                                        "resolution": "Get new token."})

        self.verify_token_data(payload)
        return payload

        # if await is_token_revoked(payload.get("jti")):
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    @staticmethod
    def is_valid_token(token: str) -> bool:
        payload = decode_jwt_token(token)
        return payload is not None

    def verify_token_data(self, payload: dict):
        raise NotImplementedError("This method is not implemented please override this method in subclass.")


class AccessTokenBearer(TokenBearer):

    def verify_token_data(self, payload: dict):
        if payload and payload.get("refresh"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access token required")


class RefreshTokenBearer(TokenBearer):

    def verify_token_data(self, payload: dict):
        if payload and not payload.get("refresh"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token required")


# def RoleChecker(allowed_roles: List[str]):
#     class RoleBearer(AccessTokenBearer):
#         def verify_token_data(self, token_data: dict):
#             super().verify_token_data(token_data)
#             if token_data.get("role") not in allowed_roles:
#                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
#     return RoleBearer()


#################--------Dependencies-----------########################

access_token_bearer = AccessTokenBearer()
AccessTokenDep = Depends(access_token_bearer)

refresh_token_bearer = RefreshTokenBearer()
RefreshTokenDep = Depends(refresh_token_bearer)
