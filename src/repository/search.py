from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.cloudinary import configure_cloudinary
from src.entity.models import Post, User, TagToPost, Tag

from src.schemas.post import PostModel
from src.repository.tags import get_or_create_tag_by_name
from src.schemas.tag import TagUpdate


async def get_post_by_tag(filter_by_date: bool, filter_by_rating: bool, tag: str, db: AsyncSession):
    post = select(Post).join(Post.tags).filter(Tag.name == tag)
    if filter_by_date:
        post = post.order_by(Post.created_at.desc())
    if filter_by_rating:
        post = post.order_by(Post.rating.desc())
    post = await db.execute(post)
    return post.scalars().unique().all()


async def get_post_by_keyword(filter_by_date: bool, filter_by_rating: bool, keyword: str, db: AsyncSession):
    post = select(Post).where(Post.name.like(f'%{keyword}%'))
    if filter_by_date:
        post = post.order_by(Post.created_at.desc())
    if filter_by_rating:
        post = post.order_by(Post.rating.desc())
    post = await db.execute(post)
    return post.scalars().unique().all()


async def get_post_by_user(filter_by_date: bool, filter_by_rating: bool, username: str, db: AsyncSession):
    post = select(Post).join(Post.user).filter(User.username == username)
    if filter_by_date:
        post = post.order_by(Post.created_at.desc())
    if filter_by_rating:
        post = post.order_by(Post.rating.desc())
    post = await db.execute(post)
    return post.scalars().unique().all()
