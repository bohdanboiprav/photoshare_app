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
    post = await repository_search.get_post_by_tag(filter_by_date, filter_by_rating, tag, db)
    return post


@router.get("/by_keyword/{keyword}", response_model=List[PostResponse])
async def get_post_by_keyword(filter_by_date: bool = True,
                              filter_by_rating: bool = False,
                              keyword: str = Path(),
                              current_user: User = Depends(auth_service.get_current_user),
                              db: AsyncSession = Depends(get_db)):
    post = await repository_search.get_post_by_keyword(filter_by_date, filter_by_rating, keyword, db)
    return post


@router.get("/by_user/{username}", response_model=List[PostResponse])
async def get_post_by_keyword(filter_by_date: bool = True,
                              filter_by_rating: bool = False,
                              username: str = Path(),
                              current_user: User = Depends(auth_service.get_current_user),
                              db: AsyncSession = Depends(get_db)):
    if current_user.user_type == 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=messages.NO_PERMISSIONS)
    post = await repository_search.get_post_by_user(filter_by_date, filter_by_rating, username, db)
    return post
