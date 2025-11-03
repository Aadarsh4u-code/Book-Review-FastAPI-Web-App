# API endpoints (/login, /register, /verify-email)
from datetime import timezone, datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.auth.dependencies import RefreshTokenDep
from app.core.security import verify_password, create_jwt_token
from app.user.dependencies import UserServiceDep
from app.user.models import UserModel
from app.user.schemas import UserCreate, UserBase, UserLogin

auth_router = APIRouter()


# Register User
@auth_router.post("/signup", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def signup(form_data: UserCreate, service: UserServiceDep) -> UserModel:
    existing_user = await service.check_user_exists(form_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with email already exists"
        )
    new_user = await service.create_user(form_data)
    return new_user


# Login / generate access + refresh tokens
@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(form_data: UserLogin, service: UserServiceDep) -> JSONResponse:
    user_data = await service.get_user_by_email(form_data.email)
    if user_data is not None:
        is_valid_password = verify_password(form_data.password, user_data.hashed_password)
        if is_valid_password:
            user_data_dict = {
                "uid": str(user_data.uid),
                "email": user_data.email,
                "role": user_data.role
            }
            access_token = create_jwt_token(user_data_dict)
            refresh_token = create_jwt_token(user_data_dict, refresh=True)

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "Bearer",
                    "user_details": {
                        "uid": str(user_data.uid),
                        "email": user_data.email,
                    }

                },
                status_code=status.HTTP_200_OK,
            )

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials.")


# refresh expired access token
@auth_router.post("/refresh_token", status_code=status.HTTP_200_OK)
async def get_new_access_token(token_details: dict = RefreshTokenDep) -> JSONResponse:
    expiry_timestamp = token_details.get("exp")
    if expiry_timestamp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing expiration")
    if datetime.now(timezone.utc).timestamp() < expiry_timestamp:
        new_access_token = create_jwt_token(user_data=token_details.get("user"))
        return JSONResponse(content={
            "access_token": new_access_token
        })
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
