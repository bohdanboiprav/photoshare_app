from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User, Post


async def get_profile(user: User, db: AsyncSession) -> dict:
    result = {}
    if user:
        stmt = select(func.count()).where(Post.user_id == user.id)
        count = await db.execute(stmt)
        posts_count = count.scalar()

        result = {
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            # "comments_count": comments_count,
            "posts_count": posts_count,
            "created_at": user.created_at,
        }
    return result
