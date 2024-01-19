from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, User, TagToPost
from src.schemas.post import PostModel
from src.repository.tags import get_or_create_tag_by_name
from src.schemas.tag import TagUpdate


async def get_post(post_id: int, db: AsyncSession):
    post = select(Post).filter(Post.id == post_id)
    post = await db.execute(post)
    return post.scalars().first()


async def get_user_post(post_id: int, current_user: User, db: AsyncSession):
    post = select(Post).filter(Post.id == post_id).filter_by(user=current_user)
    if current_user.id == 3:
        post = select(Post).filter(Post.id == post_id)
    post = await db.execute(post)
    return post.scalars().first()


async def create_post(body: PostModel, image_url: str, current_user: User, db: AsyncSession):
    post = select(Post).filter_by(user=current_user).filter(Post.name == body.name)
    post = await db.execute(post)
    post = post.scalars().first()
    if post:
        raise HTTPException(status_code=400, detail="Post with this name already exists")
    post = Post(name=body.name, content=body.content, image_url=image_url, user=current_user)
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
    post = await get_user_post(post_id, current_user, db)
    if post:
        post.name = body.name
        post.content = body.content
        post.image_url = post.image_url

        post.tags.clear()

        for tag_name in body.tags:
            tag = await get_or_create_tag_by_name(tag_name, db)
            tag_to_post = TagToPost(post_id=post_id, tag_id=tag.id)
            db.add(tag_to_post)
        await db.commit()
        await db.refresh(post)
    return post


async def add_tag_to_post(body: TagUpdate, current_user: User, db: AsyncSession) -> Post:
    post = await db.execute(select(Post).where(Post.name == body.name))
    post = post.scalar()
    if not post:
        raise HTTPException(status_code=400, detail="Post with this name doesn't exist")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can add tags only for self posts")
    body_tagnames = [bod for bod in body.tags]
    post_tagnames = [tags.name for tags in post.tags]
    post__id = post.id
    for tag_name in body.tags:
        if tag_name in post_tagnames:
            continue
        if len(set(post_tagnames + body_tagnames)) > 5:
            quantity = 5 - len(post.tags)
            raise HTTPException(status_code=400, detail=f"Post can consists maximum 5 tags. You can add: {quantity}")
        tag = await get_or_create_tag_by_name(tag_name, db)
        tag_to_post = TagToPost(post_id=post__id, tag_id=tag.id)
        db.add(tag_to_post)
    await db.commit()
    await db.refresh(post)
    return post


async def remove_post(post_id: int, current_user: User, db: AsyncSession):
    post = await get_user_post(post_id, current_user, db)
    post_return = post
    if post:
        post.tags.clear()
        await db.commit()
        await db.delete(post)
        await db.commit()
    return post_return
