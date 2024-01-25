from fastapi import HTTPException

from sqlalchemy import select, func, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, User, TagToPost ,PhotoUrl
from src.schemas.transformation import PhotoResponse
from src.repository.tags import get_or_create_tag_by_name
from src.schemas.tag import TagUpdate
from typing import List

async def get_photo_info(id: int, current_user: User,  db: AsyncSession):
    photo = select(Post).filter_by(user=current_user).filter(Post.id == id)
    photo = await db.execute(photo)
    return photo.scalars().first()

async def get_photo_info_qr(id: int,current_user: User, db: AsyncSession):
    post = await get_photo_info(id, current_user, db)
    id = post.id
    photo = select(PhotoUrl).filter_by(post_id=id)
    photos = await db.execute(photo)
    return photos.scalars().first()

async def update_qr(id: int, url: str,url_qr:str , db: AsyncSession):
    update_url = select(PhotoUrl).filter_by(transform_url=url)
    update_url = await db.execute(update_url)
    update_url = update_url.scalars().first()
    if update_url:
        if update_url.transform_url_qr:
            raise HTTPException(status_code=400, detail="URL and Qrcode URL with this transformation already exists")
        else:
            if url_qr != None:
                update_url.transform_url = url
                update_url.transform_url_qr = url_qr
                await db.commit()
                await db.refresh(update_url)
            else:
                raise HTTPException(status_code=400, detail="URL  with this transformation already exists")
    else:
        update_url = PhotoUrl(transform_url=url, transform_url_qr=url_qr, post_id=id)
        db.add(update_url)
        await db.commit()
        await db.refresh(update_url)
    return update_url
    

async def get_photo_url(id, current_user: User, db: AsyncSession) -> List[PhotoUrl]:
    photo = select(Post).filter_by(user=current_user).filter_by(id=id)
    photo = await db.execute(photo)
    return photo.scalars().first()


async def get_all_url(limit: int, offset: int, current_user: User, db: AsyncSession) -> List[PhotoUrl]:
    photo = select(Post).filter_by(user=current_user).offset(offset).limit(limit)
    photo = await db.execute(photo)
    return photo.scalars().unique().all()

