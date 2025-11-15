import uuid
from fastapi import HTTPException,status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.service import BookService
from src.reviews.models import ReviewModel
from src.reviews.schemas import ReviewCreate
from src.user.service import UserService
from src.core.logger import logger


class ReviewService:
    def __init__(self, db_session: AsyncSession, user_service: UserService, book_service: BookService):
        self.db = db_session
        self.user_service = user_service
        self.book_service = book_service

    async def add_review_to_book(self, review_data: ReviewCreate, book_uid: uuid.UUID, user_email: EmailStr) -> ReviewModel:
        try:
            # use the injected services instead of global calls
            book = await self.book_service.get_book(book_uid)
            if not book:
                raise HTTPException(
                    detail="Book not found", status_code=status.HTTP_404_NOT_FOUND
                )

            user = await self.user_service.get_user_by_email(user_email)
            if not user:
                raise HTTPException(
                    detail="User not found", status_code=status.HTTP_404_NOT_FOUND
                )
            # new_review = ReviewModel(**review_dict, user_uid=user.uid, book_uid=book.bid)
            print(" New review book -----------", book.bid, book.title)
            print(" New review user -----------", user)
            new_review = ReviewModel(
                review_text=review_data.review_text,
                rating=review_data.rating,
                book_uid=book.bid,
                user_uid=user.uid
            )

            print(" New review -----------",new_review)
            # review.book_uid = book_uid
            # review.user_email = user_email
            self.db.add(new_review)
            await self.db.flush()  # make sure PK is generated
            await self.db.refresh(new_review)
            return new_review
        except Exception as e:
            logger.error(f"Failed to add Review: {e}")
            raise HTTPException(
                detail="Oops... something went wrong!",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
