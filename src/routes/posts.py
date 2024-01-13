from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import ValidationError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repository import posts as repository_posts
from src.schemas.posts import PostModel, PostResponse
from src.schemas.tags import TagResponse, TagUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostModel,
    db: AsyncSession = Depends(get_db),
):
    post = await repository_posts.create_post(body, db)
    return post


@router.post("/add", response_model=TagResponse)
async def add_tags_to_post(body: TagUpdate, db: AsyncSession = Depends(get_db)):
    tag = await repository_posts.add_tag_to_post(body, db)
    return tag

