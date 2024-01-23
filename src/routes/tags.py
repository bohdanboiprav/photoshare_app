from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.repository import tags as repository_tags
from src.schemas.tag import TagResponse, TagModel, TagUpdate
from src.services.auth import auth_service

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
        body: TagModel,
        db: AsyncSession = Depends(get_db),
):
    """
    The create_tag function creates a new tag in the database.

    :param body: TagModel: Specify the type of data that is expected in the request body
    :param db: AsyncSession: Pass the database connection to the repository
    :param : Get the id of the tag to be deleted
    :return: A tagmodel object
    :doc-author: Trelent
    """
    return await repository_tags.create_tag(body, db)


@router.get("/all", response_model=list[TagResponse])
async def get_all_tags(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db)):
    """
    The get_all_tags function returns a list of all tags in the database.

    :param limit: int: Limit the number of tags returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of tags returned
    :param offset: int: Offset the query by a certain amount
    :param ge: Specify a minimum value for the limit parameter
    :param db: AsyncSession: Get the database session
    :return: A list of tags
    :doc-author: Trelent
    """
    tags = await repository_tags.get_all_tags(limit, offset, db)
    return tags


@router.get("/{name}", response_model=TagResponse)
async def get_or_create_tag_by_name(name: str, db: AsyncSession = Depends(get_db)):
    """
    The get_or_create_tag_by_name function is a helper function that will either return an existing tag
        or create a new one if it doesn't exist. This is useful for when you want to add tags to an article, but
        don't want to have duplicate tags in the database.

    :param name: str: Specify the name of the tag to be created
    :param db: AsyncSession: Pass the database session to the function
    :return: A tuple of the tag object and a boolean value
    :doc-author: Trelent
    """
    tag = await repository_tags.get_or_create_tag_by_name(name, db)
    return tag


@router.delete("/{tag_name}", response_model=TagResponse)
async def remove_tag(tag_name: str, user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    The remove_tag function removes a tag from the database.

    :param tag_name: str: Get the tag name from the request
    :param user: User: Get the user object from the token
    :param db: AsyncSession: Get the database connection
    :return: A tag object (see the repository_tags
    :doc-author: Trelent
    """
    if user.user_type_id == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin/moder can remove tags")
    tag = await repository_tags.get_tag(tag_name, db)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag is not found")
    removed_tag = await repository_tags.remove_tag(tag, db)
    return removed_tag
