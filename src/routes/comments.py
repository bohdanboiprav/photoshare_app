from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.routes.users import get_current_user
from src.schemas.comment import CommentModel, CommentResponse
from src.repository import comments
from src.services.auth import auth_service

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CommentModel,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    return await comments.create_comment(body, current_user, db)

#
# @router.get("/", response_model=list[CommentResponse])
# async def get_comments(
#         limit: int = Query(10, ge=10, le=500),
#         offset: int = Query(0, ge=0),
#         db: AsyncSession = Depends(get_db)):
#     return await comments.get_comments(limit, offset, db)

#
# @router.get("/{comment_id}", response_model=CommentResponse)
# async def get_comment(
#         comment_id: int = Path(ge=1),
#         db: AsyncSession = Depends(get_db)):
#     return await comments.get_comment(comment_id, db)

#
# @router.put("/{comment_id}", response_model=CommentResponse, )
# async def update_comment(
#         comment_id: int = Path(ge=1),
#         body: CommentModel = Body(),
#         current_user: User = Depends(get_current_user),
#         db: AsyncSession = Depends(get_db)):
#     return await comments.update_comment(comment_id, body, current_user, db)
#
#
# @router.delete("/{comment_id}", response_model=CommentResponse)
# async def delete_comment(
#         comment_id: int = Path(ge=1),
#         current_user: User = Depends(get_current_user),
#         db: AsyncSession = Depends(get_db)):
#     return await comments.delete_comment(comment_id, current_user, db)
#
