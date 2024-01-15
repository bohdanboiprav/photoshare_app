from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Tag
from src.schemas.tag import TagModel


async def create_tag(body: TagModel, db: AsyncSession) -> Tag:
    tag = await db.execute(select(Tag).where(Tag.name == body.name))
    tag = tag.scalar()
    if tag:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    tag = Tag(name=body.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def get_all_tags(limit, offset, db: AsyncSession) -> List[Tag]:
    stmt = select(Tag).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def get_or_create_tag_by_name(tag_name: str, db: AsyncSession) -> Tag:
    tag = await db.execute(select(Tag).where(Tag.name == tag_name))
    tag = tag.scalars().first()
    if tag:
        print("Exist")
        return tag
    else:
        print("NOT Exist")
        new_tag = Tag(name=tag_name)
        db.add(new_tag)
        await db.commit()
        await db.refresh(new_tag)
        return new_tag
