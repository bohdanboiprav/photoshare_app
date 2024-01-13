from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Post, User, UserType
from src.schemas.user import UserModel


async def create_user(body: UserModel, db: AsyncSession):
    user = User(username=body.username, email=body.email, password=body.password, avatar=body.avatar,
                user_type_id=1)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user(username: str, db: AsyncSession):
    user = select(User).filter(User.username == username)
    user = await db.execute(user)
    return user.scalars().first()
