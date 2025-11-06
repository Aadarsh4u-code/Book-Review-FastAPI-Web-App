from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import RefreshTokenDep, AccessTokenDep, AuthServiceDep
from app.auth.schemas import MeResponse, TokenResponse, TokenPayload
from app.user.dependencies import UserServiceDep
from app.user.schemas import UserCreate, UserLogin

auth_router = APIRouter()


# Register User
@auth_router.post("/signup", response_model=MeResponse, status_code=status.HTTP_201_CREATED)
async def signup(form_data: UserCreate, user_service: UserServiceDep):
    # Check if email exists
    if await user_service.check_user_exists(form_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    # Create user
    new_user = await user_service.create_user(form_data)
    # Return serialized response model
    return MeResponse.from_user(new_user)


# Login / generate access + refresh tokens
@auth_router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(credentials: UserLogin,auth_service : AuthServiceDep):
    return await auth_service.login(email=credentials.email,password=credentials.password)


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh(auth_service: AuthServiceDep, token: TokenPayload = RefreshTokenDep):
    return await auth_service.refresh(token.model_dump())

@auth_router.post("/logout")
async def logout(auth_service: AuthServiceDep, token: TokenPayload = AccessTokenDep):
    return await auth_service.logout(token.model_dump())

@auth_router.post("/revoke")
async def revoke_all(auth_service: AuthServiceDep, token: TokenPayload = AccessTokenDep):
    return await auth_service.revoke_all(token.model_dump())

@auth_router.get("/me", response_model=MeResponse)
async def me(token: TokenPayload = AccessTokenDep):
    user = token.user
    return MeResponse(uid=user["uid"], email=user["email"], role=user["role"])


