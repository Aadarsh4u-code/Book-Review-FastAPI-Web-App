# API endpoints (/login, /register, /verify-email)

from fastapi import APIRouter, Depends, HTTPException, status

from app.user.dependencies import user_service_dep
from app.user.models import UserModel
from app.user.schemas import UserCreate, UserResponse

auth_router = APIRouter()


@auth_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, service: user_service_dep) -> UserModel:
    existing_user = await service.check_user_exists(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with email already exists"
        )
    new_user = await service.create_user(user_data)
    return new_user