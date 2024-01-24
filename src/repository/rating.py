from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Rating, Post


async def create_rating(body, postid, current_user, db):
    """
    The create_rating function creates a new rating for the post with id = postid.
        The value of the rating is given by body.value, and it is created by current_user.

    :param body: Get the value of the rating
    :param postid: Find the post that is being rated
    :param current_user: Get the id of the user who is currently logged in
    :param db: Access the database
    :return: The new rating that was created
    """
    new_rating = Rating(value=body.value, post_id=postid, user_id=current_user.id)
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)


async def get_rating(body, user, db):
    """
    The get_rating function takes in a body, user, and db.
    It then creates an SQLAlchemy statement that selects the rating of a post by the user.
    The function returns this rating.

    :param body: Get the post_id from the body of the request
    :param user: Get the user id
    :param db: Access the database
    :return: A rating object
    """
    smt = select(Rating).filter_by(post_id=body.post_id, user_id=user.id)
    rating = await db.execute(smt)
    return rating.scalars().first()


async def get_postsratings(_id, db: AsyncSession):
    """
    The get_postsratings function takes in a post id and returns all the ratings for that post.

    :param _id: Get the post id from the database
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of all the ratings for a post
    """
    post = select(Rating).where(Rating.post_id == _id)
    post = await db.execute(post)
    return post.scalars().unique().all()


async def refresh_rating(post: Post, db: AsyncSession):
    """
    The refresh_rating function takes a Post object and an AsyncSession object as arguments.
    It then uses the SQLAlchemy ORM to query the database for all ratings associated with that post,
    and calculates their average value. It then updates the rating attribute of that post with this new value,
    commits it to the database, and returns a refreshed version of that Post.

    :param post: Post: Pass the post object to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: A post object
    """
    stmt = select(func.avg(Rating.value)).where(Rating.post_id == post.id)
    result = await db.execute(stmt)
    average_rating = result.scalar()
    post.rating = average_rating
    await db.commit()
    await db.refresh(post)
    return post


async def delete_rating(post: Post, rating: Rating, db: AsyncSession):
    """
    The delete_rating function deletes a rating from the database.

    :param post: Post: Get the post that is being rated
    :param rating: Rating: Specify the rating to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :return: The post object
    """
    await db.delete(rating)
    await db.commit()
    await db.refresh(post)
    return post
