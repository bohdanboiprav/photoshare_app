from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Tag
from src.schemas.tag import TagModel


async def create_tag(body: TagModel, db: AsyncSession) -> Tag:
    """
    The create_tag function creates a new tag in the database.
        It takes a TagModel object as input and returns the created Tag object.
        If there is already an existing tag with that name, it will raise an error.

    :param body: TagModel: Get the name of the tag from the request body
    :param db: AsyncSession: Create a database session for the function
    :return: A tag object
    """
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
    """
    The get_all_tags function returns a list of all tags in the database.

    :param limit: Limit the number of results returned
    :param offset: Skip a certain number of rows
    :param db: AsyncSession: Pass the database session into the function
    :return: A list of tag objects
    """
    stmt = select(Tag).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().unique().all()


async def get_tag(tag_name, db: AsyncSession) -> Tag:
    """
    The get_tag function takes a tag name and returns the corresponding Tag object.
    If no such tag exists, it returns None.

    :param tag_name: Filter the tag table by name
    :param db: AsyncSession: Pass in the database session
    :return: A tag object
    """
    stmt = select(Tag).filter_by(name=tag_name)
    tag = await db.execute(stmt)
    return tag.scalars().unique().first()


async def get_or_create_tag_by_name(tag_name: str, db: AsyncSession) -> Tag:
    """
    The get_or_create_tag_by_name function takes a tag name and an async database session.
    It then checks if the tag exists in the database, returning it if so. If not, it creates a new Tag object with that name
    and returns that.

    :param tag_name: str: Specify the name of the tag that is being created
    :param db: AsyncSession: Pass in the database session to the function
    :return: A tag instance
    """
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


async def remove_tag(tag: Tag, db: AsyncSession):
    """
    The remove_tag function removes a tag from the database.

    :param tag: Tag: Pass in the tag object that we want to delete
    :param db: AsyncSession: Pass in the database session
    :return: The tag that was removed
    """
    await db.delete(tag)
    await db.commit()
    return tag
