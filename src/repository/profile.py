from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import User, Post, Comment
from src.schemas.user import UserSchema


async def get_profile(user: User, db: AsyncSession) -> dict:
    """
    The get_profile function returns a dictionary containing the following information:
        - username
        - email
        - avatar (url)
        - comments_count (number of comments made by user)
        - posts_count (number of posts made by user)

    :param user: User: Pass the user object to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: A dictionary of user information
    :doc-author: Trelent
    """
    result = {}
    if user:
        stmt = select(func.count()).where(Comment.user_id == user.id)
        count = await db.execute(stmt)
        comments_count = count.scalar()

        stmt = select(func.count()).where(Post.user_id == user.id)
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
    """
    The update_user_profile function updates a user's profile information.
        Args:
            body (UserSchema): The UserSchema object containing the new user data.
            user (User): The User object to be updated.

    :param body: UserSchema: Get the data from the request body
    :param user: User: Get the user object from the database
    :param db: AsyncSession: Pass in the database session
    :return: The updated user object
    :doc-author: Trelent
    """
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
