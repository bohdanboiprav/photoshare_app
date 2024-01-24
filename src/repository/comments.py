from select import select

from fastapi import HTTPException

from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.comment import CreateCommentModel, CommentUpdateModel, CommentDeleteModel
from src.entity.models import User, Comment, CommentToPost
from src.conf import messages


async def create_comment(body: CreateCommentModel, current_user: User, db: AsyncSession):
    comment = Comment(content=body.content, post_id=int(body.post_id), user_id=current_user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    comments_to_posts = CommentToPost(comment_id=comment.id, post_id=body.post_id)
    db.add(comments_to_posts)
    await db.commit()
    await db.refresh(comments_to_posts)
    return comment


async def update_comment(body: CommentUpdateModel, current_user: User, db: AsyncSession):
    """
    The update_comment function updates a comment in the database.
        It takes a CommentUpdateModel as input, which contains the id of the comment to be updated and its new content.
        The function also takes two other parameters: current_user and db.
        The current_user parameter is used to check if the user who wants to update this comment is actually its author,
        while db is an instance of AsyncSession that we use for querying our database.

    :param body: CommentUpdateModel: Get the comment_id and content from the request body
    :param current_user: User: Get the user id of the current user
    :param db: AsyncSession: Access the database
    :return: The updated comment
    :doc-author: Trelent
    """
    comment = await db.get(Comment, body.comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail=messages.COMMENT_NOT_FOUND)
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail=messages.COMMENT_NOT_PERMISSION)
    comment.content = body.content
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(body: CommentDeleteModel, user: User, db: AsyncSession):
    """
    The delete_comment function deletes a comment from the database.
        It takes in a CommentDeleteModel object, which contains the id of the comment to be deleted.
        The function then checks if the user has enough permissions to delete comments (user_type_id 2 or 3).
        If not, it raises an HTTPException with status code 403 and detail &quot;Not enough permissions&quot;.


    :param body: CommentDeleteModel: Get the comment_id from the request body
    :param user: User: Check if the user is an admin or moderator
    :param db: AsyncSession: Get the database session
    :return: The deleted comment
    :doc-author: Trelent
    """
    user_ = await db.get(User, user.id)
    if user_.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail=messages.COMMENT_NOT_PERMISSION)
    comment = await db.get(Comment, body.comment_id, options=[selectinload(Comment.comments_to_posts)])
    if not comment:
        raise HTTPException(status_code=404, detail=messages.COMMENT_NOT_FOUND)
    await db.delete(comment)
    await db.commit()
