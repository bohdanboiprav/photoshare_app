from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User, Post, Comment
from src.schemas.user import UserSchema


async def get_profile(user: User, db: AsyncSession) -> dict:
    result = {}
    if user:
        stmt = select(func.count()).where(Post.user_id == user.id)
        count = await db.execute(stmt)
        comments_count = count.scalar()

        stmt = select(func.count()).where(Comment.user_id == user.id)
        count = await db.execute(stmt)
        posts_count = count.scalar()

        result = {
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "comments_count": comments_count,
            "posts_count": posts_count,
            "created_at": user.created_at,
        }
    return result


async def update_user_profile(body: UserSchema, user: User, db: AsyncSession) -> User | None:
    stmt = select(User).filter_by(username=user.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        user.username = body.username
        user.email = body.email
        user.password = body.password
        user.updated_at = datetime.now()
        await db.commit()
        await db.refresh(user)
    return user
