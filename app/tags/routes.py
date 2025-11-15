import uuid
from typing import List
from fastapi import APIRouter, status, HTTPException

from app.auth.dependencies import get_role_checker_dep
from app.books.models import BookModel
from app.books.schemas import BookResponse
from app.shared.exception_handlers import TagAlreadyExists, TagNotFound, BookNotFound
from app.shared.utils import UserRole
from app.tags.dependencies import TagServiceDep
from app.tags.schemas import TagResponse, TagCreate, TagAdd

role_checker_dep = get_role_checker_dep([UserRole.user, UserRole.admin, UserRole.superadmin])
tags_router = APIRouter(dependencies=[role_checker_dep])


@tags_router.get("/", response_model=List[TagResponse], status_code=status.HTTP_200_OK)
async def get_all_tags(tag_service: TagServiceDep):
    return await tag_service.list_tags()


@tags_router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(tag_data: TagCreate, tag_service: TagServiceDep):
    try:
        return await tag_service.create_tag(tag_data)
    except TagAlreadyExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists")


@tags_router.get("/{tag_uid}", response_model=TagResponse)
async def get_single_tag(tag_uid: uuid.UUID, tag_service: TagServiceDep):
    tag = await tag_service.get_tag(tag_uid)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@tags_router.put("/{tag_uid}", response_model=TagResponse)
async def update_tag(tag_uid: uuid.UUID, tag_update: TagCreate, tag_service: TagServiceDep):
    try:
        return await tag_service.update_tag(tag_uid, tag_update)
    except TagNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")


@tags_router.delete("/{tag_uid}", status_code=status.HTTP_200_OK)
async def delete_tag(tag_uid: uuid.UUID, tag_service: TagServiceDep):
    try:
        result = await tag_service.delete_tag(tag_uid)
        return {"success": result, "message": "Tag deleted successfully"}
    except TagNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")


@tags_router.post("/book/{book_uid}/tags", response_model=BookResponse)
async def add_tags_to_book(
    book_uid: uuid.UUID,
    tag_data: TagAdd,
    tag_service: TagServiceDep,
):
    try:
        return await tag_service.add_tag_to_book(book_uid, tag_data)
    except BookNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
