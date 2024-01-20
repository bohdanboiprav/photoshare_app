from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.schemas.comment import CreateCommentModel, CommentResponse, CommentUpdateModel, CommentDeleteModel
from src.repository import comments
from src.services.auth import auth_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CreateCommentModel,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    return await comments.create_comment(body, current_user, db)


@router.put("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def update_comment(
        body: CommentUpdateModel,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    return await comments.update_comment(body, current_user, db)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        body: CommentDeleteModel,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    return await comments.delete_comment(body, current_user, db)
