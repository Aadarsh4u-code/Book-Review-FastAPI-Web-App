import uuid
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.auth.dependencies import AccessTokenDep, get_role_checker_dep
from app.books.models import BookModel
from app.books.dependencies import BookServiceDep
from app.books.schemas import BookUpdate, BookResponse, BookCreate
from app.core.logger import logger
from app.shared.utils import UserRole

role_checker_dep = get_role_checker_dep([UserRole.user, UserRole.admin, UserRole.superadmin])
book_router = APIRouter(dependencies=[role_checker_dep])


@book_router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def get_all_books(
        service: BookServiceDep
):
    book_list = await service.list_books()
    logger.info(f"Found {len(book_list)} books")
    if not book_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found")
    return book_list


@book_router.get("/user/{user_id}", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def get_books_by_user_submission(user_id: uuid.UUID, service: BookServiceDep):
    books = await service.get_books_by_user(user_id)
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found")
    return books



@book_router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_a_book(
        book_data: BookCreate,
        service: BookServiceDep,
        token_payload=AccessTokenDep,
) -> BookModel:
    user_uid = token_payload.get("user")['uid']
    return await service.create_book(book_data, user_uid)


@book_router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_a_book(
        service: BookServiceDep,
        book_id: uuid.UUID,
) -> BookModel:
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@book_router.patch("/{book_id}", response_model=BookUpdate)
async def update_a_book(
        book_update_data: BookUpdate,
        service: BookServiceDep,
        book_id: uuid.UUID,
) -> BookModel:
    book_to_updated = await service.update_book(book_id, book_update_data)
    if not book_to_updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book_to_updated


@book_router.delete("/{book_id}", status_code=status.HTTP_200_OK)
async def delete_a_book(
        service: BookServiceDep,
        book_id: uuid.UUID,
) -> dict:
    result = await service.delete_book(book_id)
    return {"success": result, "message": "Book deleted successfully"}
