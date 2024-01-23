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


@router.get("/{tag}", response_model=List[PostResponse])
async def get_post_by_tag(tag: str = Path(), current_user: User = Depends(auth_service.get_current_user),
                          db: AsyncSession = Depends(get_db)):
    post = await repository_search.get_post_by_tag(tag, db)
    return post
