import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from src.conf import messages
from src.conf.cloudinary import configure_cloudinary
from src.database.db import get_db
from src.entity.models import User
from src.schemas.post import PostModel, PostResponse, PostDeletedResponse
from src.repository import search as repository_search
from src.schemas.tag import TagUpdate
from src.services.auth import auth_service

router = APIRouter(prefix='/search', tags=["search"])


@router.get("/by_tag/{tag}", response_model=List[PostResponse])
async def get_post_by_tag(filter_by_date: bool = True,
                          filter_by_rating: bool = False,
                          tag: str = Path(), current_user: User = Depends(auth_service.get_current_user),
                          db: AsyncSession = Depends(get_db)):
    """
    The get_post_by_tag function is used to retrieve a post by tag.
        The function takes in the following parameters:
            - filter_by_date (bool): If true, will return posts sorted by date. Default value is True.
            - filter_by_rating (bool): If true, will return posts sorted by rating. Default value is False.
            - tag (str): The name of the tag that you want to search for a post with.

    :param filter_by_date: bool: Filter the posts by date
    :param filter_by_rating: bool: Filter the posts by rating
    :param tag: str: Specify the tag that we want to search for
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A list of posts that match the tag
    """
    post = await repository_search.get_post_by_tag(filter_by_date, filter_by_rating, tag, db)
    return post


@router.get("/by_keyword/{keyword}", response_model=List[PostResponse])
async def get_post_by_keyword(filter_by_date: bool = True,
                              filter_by_rating: bool = False,
                              keyword: str = Path(),
                              current_user: User = Depends(auth_service.get_current_user),
                              db: AsyncSession = Depends(get_db)):
    """
    The get_post_by_keyword function is used to search for a post by keyword.
        The function takes in the following parameters:
            - filter_by_date (bool): If true, will return posts that are within the last 24 hours. Default value is True.
            - filter_by_rating (bool): If true, will return posts with a rating of at least 3 stars. Default value is False.
            - keyword (str): The string to be searched for in all post titles and descriptions.

    :param filter_by_date: bool: Determine whether the search should be filtered by date or not
    :param filter_by_rating: bool: Filter the posts by rating
    :param keyword: str: Search for a post by keyword
    :param current_user: User: Get the current user from the database
    :param db: AsyncSession: Get a database session
    :return: The post that matches the keyword
    """
    post = await repository_search.get_post_by_keyword(filter_by_date, filter_by_rating, keyword, db)
    return post


@router.get("/by_user/{username}", response_model=List[PostResponse])
async def get_post_by_keyword(filter_by_date: bool = True,
                              filter_by_rating: bool = False,
                              username: str = Path(),
                              current_user: User = Depends(auth_service.get_current_user),
                              db: AsyncSession = Depends(get_db)):
    """
    The get_post_by_keyword function is used to get a post by keyword.
        The function takes in the following parameters:
            - filter_by_date (bool): A boolean value that determines whether or not to filter posts by date.
            - filter_by_rating (bool): A boolean value that determines whether or not to sort posts by rating.
            - username (str): The username of the user whose post you want returned.

    :param filter_by_date: bool: Filter the posts by date
    :param filter_by_rating: bool: Filter the posts by rating
    :param username: str: Get the username of the user that is being searched for
    :param current_user: User: Get the user that is currently logged in
    :param db: AsyncSession: Get the database session
    :return: A list of posts that contain the keyword in their title or description
    """
    if current_user.user_type == 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=messages.NO_PERMISSIONS)
    post = await repository_search.get_post_by_user(filter_by_date, filter_by_rating, username, db)
    return post
