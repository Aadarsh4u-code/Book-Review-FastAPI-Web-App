import uuid
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.books.models import Book
from app.books.dependencies import book_service_dep
from app.books.schemas import BookUpdate, BookRead, BookCreate


book_router = APIRouter()


@book_router.get("/", response_model=List[BookRead], status_code=status.HTTP_200_OK)
async def get_all_books(service: book_service_dep):
    book_list = await service.list_books()
    if not book_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No books found")
    print('book list', book_list)
    return book_list


@book_router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_a_book(book_data: BookCreate, service: book_service_dep) -> Book:
    return await service.create_book(book_data)


@book_router.get("/{book_id}", response_model=BookRead, status_code=status.HTTP_200_OK)
async def get_a_book(service: book_service_dep, book_id: uuid.UUID) -> Book:
    book = await service.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@book_router.patch("/{book_id}", response_model=BookUpdate)
async def update_a_book(book_update_data: BookUpdate, service: book_service_dep, book_id: uuid.UUID) -> Book:
    book_to_updated = await service.update_book(book_id, book_update_data)
    if not book_to_updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book_to_updated


@book_router.delete("/{book_id}", status_code=status.HTTP_200_OK)
async def delete_a_book(service: book_service_dep, book_id: uuid.UUID) -> dict:
    success = await service.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')
    return {"ok": "Book deleted successfully."}
