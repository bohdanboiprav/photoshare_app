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
    """
    The create_comment function creates a new comment.

    :param body: CreateCommentModel: Validate the request body
    :param current_user: User: Get the user who is currently logged in
    :param db: AsyncSession: Pass the database session to the create_comment function
    :return: A comment object
    :doc-author: Trelent
    """
    return await comments.create_comment(body, current_user, db)


@router.put("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def update_comment(
        body: CommentUpdateModel,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    """
    The update_comment function updates a comment in the database.
        The function takes in a CommentUpdateModel object, which contains the id of the comment to be updated and its new body.
        It also takes in an optional current_user parameter, which is used to verify that the user making this request is authorized to do so.
        Finally, it takes an optional db parameter for dependency injection purposes.

    :param body: CommentUpdateModel: Get the data from the request body
    :param current_user: User: Get the user who is making the request
    :param db: AsyncSession: Pass the database session to the
    :return: A commentmodel object
    :doc-author: Trelent
    """
    return await comments.update_comment(body, current_user, db)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        body: CommentDeleteModel,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    """
    The delete_comment function deletes a comment from the database.
        The function takes in a CommentDeleteModel object, which contains the id of the comment to be deleted.
        It also takes in an optional current_user parameter, which is used to verify that only users who created comments can delete them.
        Finally, it takes in an optional db parameter for accessing the database.

    :param body: CommentDeleteModel: Get the comment id from the request body
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A dict with the following keys:
    :doc-author: Trelent
    """
    return await comments.delete_comment(body, current_user, db)
