from fastapi import HTTPException

from sqlalchemy import select, func, or_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Post, User, TagToPost ,PhotoUrl
from src.schemas.transformation import PhotoResponse
from src.repository.tags import get_or_create_tag_by_name
from src.schemas.tag import TagUpdate
from typing import List

async def get_photo_info(id: int, current_user: User,  db: AsyncSession):
    """
    Creates a database query to obtain information about a photo of a registered user.

    :param id: Post number with photo for transformation.
    :type id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The user to retrieve post for.
    :type current_user: User
    :return: Photo information
    :rtype: Post
    """
    photo = select(Post).filter_by(user=current_user).filter(Post.id == id)
    photo = await db.execute(photo)
    return photo.scalars().first()

# async def get_photo_info_qr(id: int,current_user: User, db: AsyncSession):
#     """
#     Creates a database query to obtain information about a photo of a registered user.

#     :param id: Post number with photo for transformation.
#     :type id: int
#     :param db: The database session.
#     :type db: Session
#     :param user: The user to retrieve post for.
#     :type user: User
#     :return: Photo information
#     :rtype: Post
#     """
#     post = await get_photo_info(id, current_user, db)
#     id = post.id
#     photo = select(PhotoUrl).filter_by(post_id=id)
#     photos = await db.execute(photo)
#     return photos.scalars().first()

async def update_qr(id: int, url: str, url_qr: str , db: AsyncSession):
    """
    Checks the information about the photo transformation in the database.
    If there is no information about the link to the transformation, 
    creates a field with info in the table. Checks for the presence of information 
    about the link to the Qrcode, if it is not there, creates a link.

    :param id: Post number with photo for transformation.
    :type id: int
    :param url: Link to photo transformation.
    :type url: str
    :param url_qr: Link to Qrcode
    :type url_qr: str
    :param db: The database session.
    :type db: Session
    :return: A list of URL.
    :rtype: list
    """
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
    
    # photo = await get_photo_info_qr(id , db)
    # if photo:
    #     photo.transform_url = url
    #     photo.transform_url_qr = url_qr
    #     await db.commit()
    #     await db.refresh(photo)
    # return photo

# async def create_post(body: PostModel, image_url: str, current_user: User, db: AsyncSession):
#     post = select(Post).filter_by(user=current_user).filter(Post.name == body.name)
#     post = await db.execute(post)
#     post = post.scalars().first()
#     if post:
#         raise HTTPException(status_code=400, detail="Post with this name already exists")
#     post = Post(name=body.name, content=body.content, image=image_url, user=current_user)
#     db.add(post)
#     await db.commit()
#     await db.refresh(post)
#     post_id = post.id
#     for tag_name in body.tags:
#         tag = await get_or_create_tag_by_name(tag_name, db)
#         tag_to_post = TagToPost(post_id=post_id, tag_id=tag.id)
#         db.add(tag_to_post)
#     await db.commit()
#     await db.refresh(post)
#     return post



async def get_photo_url(id, current_user: User, db: AsyncSession) -> List[PhotoUrl]:
    """
    Creates a database query to obtain information about a photo of a registered user.

    :param id: Post number with photo for transformation.
    :type id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The user to retrieve post for.
    :type current_user: User
    :return: Photo information
    :rtype: Post
    """
    photo = select(Post).filter_by(user=current_user).filter_by(id=id)
    photo = await db.execute(photo)
    return photo.scalars().first()


async def get_all_url(limit: int, offset: int, current_user: User, db: AsyncSession) -> List[PhotoUrl]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param offset: The number of contacts to skip.
    :type offset: int
    :param limit: The maximum number of cntacts to return.
    :type limit: int
    :param current_user: The user to retrieve post for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: A list of URL Post.
    :rtype: List[Post URL]
    """
    photo = select(Post).filter_by(user=current_user).offset(offset).limit(limit)
    photo = await db.execute(photo)
    return photo.scalars().unique().all()

