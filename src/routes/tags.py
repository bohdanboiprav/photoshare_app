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
    return await repository_tags.create_tag(body, db)


@router.get("/all", response_model=list[TagResponse])
async def get_all_tags(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db)):
    tags = await repository_tags.get_all_tags(limit, offset, db)
    return tags


@router.get("/{name}", response_model=TagResponse)
async def get_or_create_tag_by_name(name: str, db: AsyncSession = Depends(get_db)):
    tag = await repository_tags.get_or_create_tag_by_name(name, db)
    return tag


@router.delete("/{tag_name}", response_model=TagResponse)
async def remove_tag(tag_name: str, user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    if user.user_type_id == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin/moder can remove tags")
    tag = await repository_tags.get_tag(tag_name, db)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag is not found")
    removed_tag = await repository_tags.remove_tag(tag, db)
    return removed_tag
