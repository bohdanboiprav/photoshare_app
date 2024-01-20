from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Post, Rating
from src.repository.posts import get_post
from src.repository.rating import create_rating, get_rating
from src.schemas.post import PostResponse
from src.schemas.rating import RateModel, RateResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/rating', tags=["rating"])


@router.post("/", response_model=RateResponse)
async def rate_post(body: RateModel, current_user: User = Depends(auth_service.get_current_user),
                    db: AsyncSession = Depends(get_db)):
    post = await get_post(body.post_id, db)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="You can't rate self post")
    existed_rating = await get_rating(body, current_user, db)
    if existed_rating:
        raise HTTPException(status_code=404, detail="Rate already exist")
    new_rating = await create_rating(body, post.id, current_user, db)
    return new_rating
