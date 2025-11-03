from typing import List

from fastapi import APIRouter, status

from .schemas import UserCreate

user_router = APIRouter()

# @user_router.post("/",  status_code=status.HTTP_201_CREATED)
# async def create_user(user_data: UserCreate):
#     pass