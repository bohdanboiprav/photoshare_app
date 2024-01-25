import io
from PIL import Image, ImageDraw
from typing import List

import json
import qrcode

import cloudinary
import cloudinary.uploader
import cloudinary.api

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Query,
)
from fastapi_limiter.depends import RateLimiter

from src.conf import messages
from src.conf.cloudinary import configure_cloudinary
from src.conf.transformation import TRANSFORMATIONS
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.transformation import PhotoResponse, UrlResponse
from src.database.db import get_db
from src.repository import transformation as ts
from src.entity.models import User
from src.services.auth import auth_service

router = APIRouter(prefix="/transformation", tags=["transformation"])
configure_cloudinary()


async def url_qr_prefix(list_tr):
    """
    The url_qr_prefix function takes a list of strings and returns the concatenation of all non-None elements in that list.
        This is used to create the prefix for a QR code URL, which will be appended with an ID number.

    :param list_tr: Store the list of parameters that are used in the url_qr_prefix function
    :return: The prefix of the url, which is the first part of a url
    """
    prefix = ""
    for i in list_tr:
        if i != None:
            prefix += i
    return prefix


async def create_qr(url_transform):
    """
    The create_qr function takes a url_transform as an argument and returns
    a QR code image. The function uses the qrcode library to create a QR code
    object, add data to it, make it fit the size of the data added, and then
    create an image from that object. The function then saves that image into
    an io BytesIO object which is returned by the function.

    :param url_transform: Pass the url to be transformed into a qr code
    :return: A byte array
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url_transform)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format=img.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr


@router.get("/ping_cloudinary", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def ping_cloudinary():
    """
    The ping_cloudinary function is a simple function that pings the Cloudinary API to ensure it's working properly.
        It returns a dictionary with information about the ping.

    :return: A dictionary
    """
    ping = cloudinary.api.ping()
    print(ping)
    return ping


@router.get("/info_all_transformation", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def info_all_transformation():
    """
    The info_all_transformation function returns a dictionary of all the transformations that are available in this
        module. The keys are the names of each transformation, and the values are dictionaries containing information about
        each transformation. Each value dictionary contains three key-value pairs: 'description', which is a string
        describing what the function does; 'parameters', which is an array of strings listing all parameters for that
        function; and 'returns', which describes what type(s) will be returned by that function.

    :return: A list of all transformations
    """
    return TRANSFORMATIONS


@router.post("/transformation_photo", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def transformation_photo(
        id: int,
        create_qrcode: bool,
        transformation_1: str,
        transformation_2: str | None = None,
        transformation_3: str | None = None,
        transformation_4: str | None = None,
        transformation_5: str | None = None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)):
    """
    The transformation_photo function takes the id of a photo, and returns the original url,
    the transformed url and qr code for this photo.


    :param id: int: Identify the photo in the database
    :param create_qrcode: bool: Create a qr code for the transformed image
    :param transformation_1: str: Specify the first transformation
    :param transformation_2: str | None: Pass the transformation_2 parameter to the function
    :param transformation_3: str | None: Specify that the transformation_3 parameter is optional
    :param transformation_4: str | None: Pass the transformation_4 parameter to the function
    :param transformation_5: str | None: Pass the fifth transformation
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user
    :return: The original photo url, the transformed photo url and the qr code url
    """
    info_photo = await ts.get_photo_info(id, user, db)
    if info_photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    list_tr = [transformation_1, transformation_2, transformation_3, transformation_4, transformation_5]
    for i in list_tr:
        if i not in TRANSFORMATIONS and i != None:
            if i != None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transformation '{i}' not found")

    public_id = info_photo.image_id
    status_cloudinary = await ping_cloudinary()
    if status_cloudinary.get("status") != "ok":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Service Cloudinary is unavailable")
    all_info_photo = cloudinary.api.resource(public_id)
    url_origin = all_info_photo.get('secure_url')
    url_transform = cloudinary.CloudinaryImage(public_id).build_url(transformation=
    [
        TRANSFORMATIONS.get(transformation_1),
        TRANSFORMATIONS.get(transformation_2),
        TRANSFORMATIONS.get(transformation_3),
        TRANSFORMATIONS.get(transformation_4),
        TRANSFORMATIONS.get(transformation_5),
    ])
    prefix = url_qr_prefix(list_tr)
    url_qr = None
    if create_qrcode == True:
        img = await create_qr(url_transform)
        prefix = await url_qr_prefix(list_tr)
        publick_url_qr = f"{public_id}_{prefix}_qr"
        result = cloudinary.uploader.upload(img, public_id=publick_url_qr, owerite=True)
        url_qr = cloudinary.CloudinaryImage(publick_url_qr).build_url(version=result.get("version"))
    await ts.update_qr(id, url_transform, url_qr, db)
    return url_origin, url_transform, url_qr


# @router.post("/manual_transformation_photo",dependencies=[Depends(RateLimiter(times=2, seconds=5))])
# async def manual_transformation_photo(id: str ,transformation:str,user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
#     info_photo = await ts.get_photo_info(id, db)
#     if info_photo is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")

# @router.post("/create_qrcode_url", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
# async def create_qrcode_url(id, url_transform: str, user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
#     info_photo = await ts.get_photo_info( id, user, db)
#     if info_photo is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
#     public_id = info_photo.image
#     url_qr = f"{public_id}_qr"
#     await ts.update_qr(id , url_transform, url_qr, db)
#     return public_id

@router.post("/show_photo_url", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def show_photo_url(id: int, user: User = Depends(auth_service.get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """
    The show_photo_url function returns the photo url of a contact.

    :param id: int: Get the id of the contact
    :param user: User: Get the current user, and the db: asyncsession parameter is used to get a database session
    :param db: AsyncSession: Pass the database connection to the function
    :return: A string
    """
    result = await ts.get_photo_url(id, user, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result


@router.get("/show_all_url",response_model=List[PhotoResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def show_all_url(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    The show_all_url function returns a list of all the URLs in the database.
        The limit and offset parameters are used to paginate through results.
        The user parameter is used to ensure that only URLs belonging to the current user are returned.

    :param limit: int: Limit the number of results returned
    :param ge: Set the minimum value of a parameter
    :param le: Limit the number of results returned
    :param offset: int: Specify the number of records to skip before starting to return the results
    :param ge: Specify the minimum value of a parameter
    :param user: User: Get the user from the auth_service
    :param db: AsyncSession: Get the database connection
    :return: All the urls of a user
    """
    result = await ts.get_all_url(limit, offset, user, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result


#@router.delete("/remove_qrcode",dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def remove_qrcode(id: int, user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Creates a database query to obtain information about all photo links of a registered user.
    
    :param id: Post number with photo for transformation.
    :type id: int
    :param user: The user to retrieve post for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Links to transform photos
    :rtype: List[PhotoResponse]
    """
    post = await ts.info_qrcode_url(id, user, db)
    for i in post:
        print(i)
        cloudinary.uploader.destroy(str(i))
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND)
    return post
