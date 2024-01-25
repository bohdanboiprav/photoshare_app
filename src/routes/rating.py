from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Post, Rating
from src.repository.posts import get_post
from src.repository.rating import create_rating, get_rating, refresh_rating, delete_rating, get_postsratings
from src.repository.users import get_user_by_username
from src.schemas.post import PostResponse
from src.schemas.rating import RateModel, RateResponse, FindRateModel, AdminRateResponse, AdminPostResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/rating', tags=["rating"])


@router.post("/", response_model=PostResponse)
async def rate_post(body: RateModel, current_user: User = Depends(auth_service.get_current_user),
                    db: AsyncSession = Depends(get_db)):
    """
    The rate_post function is used to rate a post.
        It takes the following parameters:
            - body: The RateModel object containing the rating and post_id of the rated post.
            - current_user: The User object representing the user who is making this request. This parameter will be automatically filled in by FastAPI's dependency injection system, which uses OpenAPI to determine what type of data should be passed into each function parameter (in this case, it knows that we need a User object). We also use Depends(auth_service.get_current_user) to tell FastAPI that it should call our auth

    :param body: RateModel: Get the post_id and rating from the request body
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get a database session
    :return: The rating of the post after adding a new rate
    """
    post = await get_post(body.post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="You can't rate self post")
    existed_rating = await get_rating(body, current_user, db)
    if existed_rating:
        raise HTTPException(status_code=404, detail="Rate already exist")
    await create_rating(body, post.id, current_user, db)
    return await refresh_rating(post, db)


@router.delete("/", response_model=PostResponse)
async def delete_rate(body: FindRateModel, current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_db)):
    """
    The delete_rate function deletes a rate from the database.
        Deletes an existing rate in the database by its id and user_name. The post's rating is also updated to reflect this change.

    :param body: FindRateModel: Get the post_id and username of the rate that we want to delete
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A post object
    """
    if current_user.user_type_id == 1:
        raise HTTPException(status_code=403, detail="Only admin/moder can remove rate from post")
    post = await get_post(body.post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    user = await get_user_by_username(body.user_name, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    rating = await get_rating(body, user, db)
    if not rating:
        raise HTTPException(status_code=404, detail="Rate not found")
    await delete_rating(post, rating, db)
    await refresh_rating(post, db)
    return post


@router.get("/{post_id}", response_model=AdminPostResponse)
async def get_ratings(post_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_db)):
    """
    The get_ratings function returns the ratings for a given post.

    :param post_id: int: Specify the type of the parameter
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A post object, which contains the ratings
    """
    post = await get_post(post_id, db)
    return post
