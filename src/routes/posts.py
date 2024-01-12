from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.post import PostModel, PostResponse
from src.repository import posts as repository_posts
# from src.services.auth import auth_service

router = APIRouter(prefix='/posts', tags=["posts"])


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int = Path(ge=1),
                   db: AsyncSession = Depends(get_db)):
    post = await repository_posts.get_post(post_id, User(), db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post


@router.post("/create", response_model=PostResponse)
async def create_post(body: repository_posts,
                      db: AsyncSession = Depends(get_db)):
    return await repository_posts.create_post(body, User(), db)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(body: PostModel, post_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db)):
    post = await repository_posts.update_post(post_id, body, User(), db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post


@router.delete("/{post_id}", response_model=PostResponse)
async def remove_post(post_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db)):
    post = await repository_posts.remove_post(post_id, User(), db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post
