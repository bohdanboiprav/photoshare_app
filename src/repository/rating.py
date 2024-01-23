from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Rating, Post


async def create_rating(body, postid, current_user, db):
    new_rating = Rating(value=body.value, post_id=postid, user_id=current_user.id)
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)


async def get_rating(body, user, db):
    smt = select(Rating).filter_by(post_id=body.post_id, user_id=user.id)
    rating = await db.execute(smt)
    return rating.scalars().first()


async def get_postsratings(_id, db: AsyncSession):
    post = select(Rating).where(Rating.post_id == _id)
    post = await db.execute(post)
    return post.scalars().unique().all()


async def refresh_rating(post: Post, db: AsyncSession):
    stmt = select(func.avg(Rating.value)).where(Rating.post_id == post.id)
    result = await db.execute(stmt)
    average_rating = result.scalar()
    post.rating = average_rating
    await db.commit()
    await db.refresh(post)
    print(post.rating)
    return post


async def delete_rating(post: Post, rating: Rating, db: AsyncSession):
    await db.delete(rating)
    await db.commit()
    await db.refresh(post)
    return post
