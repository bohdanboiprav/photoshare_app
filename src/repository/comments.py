from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.comment import CreateCommentModel, CommentUpdateModel, CommentDeleteModel
from src.entity.models import User, Comment, CommentToPost


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
    comment = await db.get(Comment, body.comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    comment.content = body.content
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(body: CommentDeleteModel, user: User, db: AsyncSession):
    user_ = await db.get(User, user.id)
    if user_.user_type_id not in (2, 3):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    comment = await db.get(Comment, body.comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    # delComment = comment
    await db.delete(comment)
    await db.commit()
    return "delComment"
