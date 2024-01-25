from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, User, Tag


async def get_post_by_tag(filter_by_date: bool, filter_by_rating: bool, tag: str, db: AsyncSession):
    """
    The get_post_by_tag function takes in a boolean value for filtering by date,
    a boolean value for filtering by rating, a tag name string and an async database session.
    It returns all posts that have the given tag.

    :param filter_by_date: bool: Filter the posts by date
    :param filter_by_rating: bool: Filter the posts by rating
    :param tag: str: Filter posts by tag
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of posts with the given tag
    :doc-author: Trelent
    """
    post = select(Post).join(Post.tags).filter(Tag.name == tag)
    if filter_by_date:
        post = post.order_by(Post.created_at.desc())
    if filter_by_rating:
        post = post.order_by(Post.rating.desc())
    post = await db.execute(post)
    return post.scalars().unique().all()


async def get_post_by_keyword(filter_by_date: bool, filter_by_rating: bool, keyword: str, db: AsyncSession):
    """
    The get_post_by_keyword function takes in a keyword, and returns all posts that contain the keyword.
    The function also takes in two optional parameters: filter_by_date and filter_by_rating. If these are set to True,
    the returned posts will be sorted by date or rating respectively.

    :param filter_by_date: bool: Filter the posts by date
    :param filter_by_rating: bool: Filter the posts by rating
    :param keyword: str: Filter the posts by name
    :param db: AsyncSession: Connect to the database
    :return: A list of posts that match the keyword
    """
    post = select(Post).where(Post.name.like(f'%{keyword}%'))
    if filter_by_date:
        post = post.order_by(Post.created_at.desc())
    if filter_by_rating:
        post = post.order_by(Post.rating.desc())
    post = await db.execute(post)
    return post.scalars().unique().all()


async def get_post_by_user(filter_by_date: bool, filter_by_rating: bool, username: str, db: AsyncSession):
    """
    The get_post_by_user function takes in a boolean value for filtering by date,
    a boolean value for filtering by rating, a username string and an async database session.
    It returns all posts made by the user with the given username.

    :param filter_by_date: bool: Determine if the posts should be filtered by date
    :param filter_by_rating: bool: Filter the posts by rating
    :param username: str: Filter the posts by username
    :param db: AsyncSession: Pass the database connection to the function
    :return: A list of posts by the user with the given username
    """
    post = select(Post).join(Post.user).filter(User.username == username)
    if filter_by_date:
        post = post.order_by(Post.created_at.desc())
    if filter_by_rating:
        post = post.order_by(Post.rating.desc())
    post = await db.execute(post)
    return post.scalars().unique().all()
