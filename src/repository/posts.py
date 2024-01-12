import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Post, User
from src.schemas.post import PostModel


async def get_post(post_id: int, current_user: User, db: AsyncSession):
    contact = select(Post).filter(Post.id == post_id)
    contact = await db.execute(contact)
    return contact.scalar_one_or_none()


async def create_post(body: PostModel, current_user: User, db: AsyncSession):
    post = Post(name=body.name, content=body.content, user_id=current_user, image=body.image, user=current_user)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def update_post(post_id: int, body: PostModel, current_user: User, db: AsyncSession):
    post = get_post(post_id, current_user, db)
    if post:
        post.name = body.name
        post.content = body.content
        post.image = body.image
        await db.commit()
        await db.refresh(post)
    return post


async def remove_post(post_id: int, current_user: User, db: AsyncSession):
    post = get_post(post_id, current_user, db)
    if post:
        await db.delete(post)
        await db.commit()
    return post