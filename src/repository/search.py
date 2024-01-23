from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.cloudinary import configure_cloudinary
from src.entity.models import Post, User, TagToPost, Tag

from src.schemas.post import PostModel
from src.repository.tags import get_or_create_tag_by_name
from src.schemas.tag import TagUpdate


async def get_post_by_tag(tag: str, db: AsyncSession):
    post = select(Post).join(Tag).filter(Tag.name == tag)
    post = await db.execute(post)
    return post.scalars().unique().all()
