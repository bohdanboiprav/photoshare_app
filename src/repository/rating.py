from sqlalchemy import select

from src.entity.models import Rating


async def create_rating(body, postid, current_user, db):
    new_rating = Rating(value=body.value, post_id=postid, user_id=current_user.id)
    db.add(new_rating)
    await db.commit()
    await db.refresh(new_rating)
    return new_rating


async def get_rating(body, user, db):
    smt = select(Rating).filter_by(post_id=body.post_id, user_id=user.id)
    rating = await db.execute(smt)
    return rating.scalars().first()
