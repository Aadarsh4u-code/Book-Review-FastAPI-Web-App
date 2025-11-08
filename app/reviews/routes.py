import uuid
from fastapi import APIRouter, status, Depends
from pydantic import EmailStr

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserBasicDetails
from app.reviews.dependencies import ReviewServiceDep
from app.reviews.schemas import ReviewResponse, ReviewCreate


reviews_router = APIRouter()



@reviews_router.post("/book/{book_uid}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_review(
    book_uid: uuid.UUID,
    review_data: ReviewCreate,
    review_service: ReviewServiceDep,
    current_user: UserBasicDetails = Depends(get_current_user)
):
    user_email: EmailStr = current_user.email
    print("********fro route", user_email)
    return await review_service.add_review_to_book(review_data, book_uid, user_email)