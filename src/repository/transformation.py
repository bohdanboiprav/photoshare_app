from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Post, User, PhotoUrl
from typing import List


async def get_photo_info(id: int, current_user: User,  db: AsyncSession):
    """
    The get_photo_info function takes in a photo id and returns the photo's information.
        Args:
            - id (int): The ID of the photo to be retrieved.
            - current_user (User): The user who is currently logged in.  This is used to ensure that only photos belonging to this user are returned.

    :param id: int: Specify the id of the photo that we want to get information about
    :param current_user: User: Get the user that is currently logged in
    :param db: AsyncSession: Pass the database session to the function
    :return: A photo, but what if the user doesn't have a photo with that id?
    """
    photo = select(Post).filter_by(user=current_user).filter(Post.id == id)
    photo = await db.execute(photo)
    return photo.scalars().first()


async def get_photo_info_qr(id: int,current_user: User, db: AsyncSession):
    """
    The get_photo_info_qr function is used to get the photo url of a post.
        Args:
            - id (int): The id of the post.
            - current_user (User): The user who is currently logged in and using the app.
            - db (AsyncSession): A database session object that allows us to execute SQL queries on our database tables.

    :param id: int: Get the id of the post
    :param current_user: User: Check if the user is logged in or not
    :param db: AsyncSession: Make a connection to the database
    :return: The photo url of the post
    """
    post = await get_photo_info(id, current_user, db)
    id = post.id
    photo = select(PhotoUrl).filter_by(post_id=id)
    photos = await db.execute(photo)
    return photos.scalars().first()


async def update_qr(id: int, url: str, url_qr:str , db: AsyncSession):
    """
    The update_qr function updates the url and qr_url of a post.
        Args:
            - id (int): The ID of the post to update.
            - url (str): The new URL for this post.

    :param id: int: Get the post id from the database
    :param url: str: Update the url in the database
    :param url_qr:str: Update the qrcode url in the database
    :param db: AsyncSession: Pass the database session to the function
    :return: A new url and qr code for the post
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
    

async def get_photo_url(id, current_user: User, db: AsyncSession) -> List[PhotoUrl]:
    """
    The get_photo_url function takes in a photo id and returns the url of that photo.
        Args:
            - id (int): The ID of the photo to be retrieved.
            - current_user (User): The user who is making this request.

    :param id: Identify the photo in the database
    :param current_user: User: Get the current user
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of photo urls
    """
    photo = select(Post).filter_by(user=current_user).filter_by(id=id)
    photo = await db.execute(photo)
    return photo.scalars().first()


async def get_all_url(limit: int, offset: int, current_user: User, db: AsyncSession) -> List[PhotoUrl]:
    """
    The get_all_url function returns a list of all the photo urls for a given user.
        Args:
            - limit (int): The number of photos to return.
            - offset (int): The starting point in the database from which to start returning photos.  This is useful for pagination purposes, so that you can get more than one page worth of results at once.  For example, if you want 20 results per page and are on page 3, then your offset would be 40 because you'd skip the first 40 results in order to get the next 20 after that.

    :param limit: int: Limit the amount of photos returned
    :param offset: int: Specify how many records to skip
    :param current_user: User: Get the current user's photo urls
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of photourl objects
    """
    photo = select(Post).filter_by(user=current_user).offset(offset).limit(limit)
    photo = await db.execute(photo)
    return photo.scalars().unique().all()

