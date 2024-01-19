from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.comment import CommentModel
from src.entity.models import Post, User, Comment, CommentToPost


async def create_comment(body: CommentModel, current_user: User, db: AsyncSession):
    comment = Comment(content=body.content, post_id=int(body.post_id), user_id=current_user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    comments_to_posts = CommentToPost(comment_id=comment.id, post_id=body.post_id)
    db.add(comments_to_posts)
    await db.commit()
    await db.refresh(comments_to_posts)
    return comment


async def update_comment(body: CommentModel, user: User, db: AsyncSession):
    # comment = body.model_dump()
    # db.add(comment)
    # await db.commit()
    # await db.refresh(comment)
    # return comment
    pass


async def delete_comment(body: CommentModel, user: User, db: AsyncSession):
    # comment = body.model_dump()
    # db.delete(comment)
    # await db.commit()
    # await db.refresh(comment)
    # return comment
    pass