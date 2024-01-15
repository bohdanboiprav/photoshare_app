from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, User, TagToPost
from src.schemas.post import PostModel
from src.repository.tags import get_or_create_tag_by_name
from src.schemas.tag import TagUpdate


async def get_post(post_id: int, current_user: User, db: AsyncSession):
    post = select(Post).filter_by(user=current_user).filter(Post.id == post_id)
    post = await db.execute(post)
    return post.scalars().first()


async def create_post(body: PostModel, image_url: str, current_user: User, db: AsyncSession):
    post = select(Post).filter_by(user=current_user).filter(Post.name == body.name)
    post = await db.execute(post)
    post = post.scalars().first()
    if post:
        raise HTTPException(status_code=400, detail="Post with this name already exists")
    post = Post(name=body.name, content=body.content, image=image_url, user=current_user)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    post_id = post.id
    for tag_name in body.tags:
        tag = await get_or_create_tag_by_name(tag_name, db)
        tag_to_post = TagToPost(post_id=post_id, tag_id=tag.id)
        db.add(tag_to_post)
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


async def add_tag_to_post(body: TagUpdate, db: AsyncSession) -> Post:
    post = await db.execute(select(Post).where(Post.name == body.name))
    post = post.scalar()
    if not post:
        raise HTTPException(status_code=400, detail="Post with this name doesn't exist")
    post_names = [tags.name for tags in post.tags]
    body_names = [bod for bod in body.tags]
    post__id = post.id
    for tag_name in body.tags:
        if tag_name in post_names:
            continue
        if len(set(post_names + body_names)) > 5:
            quantity = 5 - len(post.tags)
            raise HTTPException(status_code=400, detail=f"Post can consists maximum 5 tags. You can add: {quantity}")
        tag = await get_or_create_tag_by_name(tag_name, db)
        tag_to_post = TagToPost(post_id=post__id, tag_id=tag.id)
        db.add(tag_to_post)
    await db.commit()
    await db.refresh(post)
    return post


async def remove_post(post_id: int, current_user: User, db: AsyncSession):
    post = select(Post).filter_by(user=current_user).filter(Post.id == post_id)
    result = await db.execute(post)
    post = result.scalar_one_or_none()
    postreturn = post
    if post:
        await db.delete(post)
        await db.commit()
    return postreturn
