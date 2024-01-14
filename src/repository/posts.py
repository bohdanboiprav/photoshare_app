from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, User
from src.schemas.post import PostModel


async def get_post(post_id: int, current_user: User, db: AsyncSession):
    post = select(Post).filter_by(user=current_user).filter(Post.id == post_id)
    post = await db.execute(post)
    return post.scalar_one_or_none()


async def create_post(body: PostModel, image_url: str, current_user: User, db: AsyncSession):
    post = Post(name=body.name, content=body.content, image=image_url, user=current_user)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def update_post(post_id: int, body: PostModel, current_user: User, db: AsyncSession):
    post = await get_post(post_id, current_user, db)
    if post:
        post.name = body.name
        post.content = body.content
        post.image = body.image
        await db.commit()
        await db.refresh(post)
    return post


async def remove_post(post_id: int, current_user: User, db: AsyncSession):
    # post = await get_post(post_id, current_user, db)
    post = select(Post).filter_by(user=current_user).filter(Post.id == post_id)
    result = await db.execute(post)
    post = result.scalar_one_or_none()
    postreturn = post
    if post:
        await db.delete(post)
        await db.commit()
    return postreturn
