from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Tag, Post, TagToPost
from src.repository.tags import get_or_create_tag_by_name
from src.schemas.posts import PostModel
from src.schemas.tags import TagUpdate


async def create_post(body: PostModel, db: AsyncSession) -> Post:
    post = await db.execute(select(Post).where(Post.name == body.name))
    post = post.scalar()
    if post:
        raise HTTPException(status_code=400, detail="Post with this name already exists")
    new_post = Post(
        name=body.name,
        content=body.content)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    tag_id = new_post.id
    for tag_name in body.tags:
        tag = await get_or_create_tag_by_name(tag_name, db)
        tag_to_post = TagToPost(post_id=tag_id, tag_id=tag.id)
        db.add(tag_to_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


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
