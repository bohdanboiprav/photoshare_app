from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repository import tags as repository_tags
from src.schemas.tags import TagResponse, TagModel, TagUpdate

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


