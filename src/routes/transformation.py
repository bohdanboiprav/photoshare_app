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
    Path
)
from src.conf import messages
from fastapi_limiter.depends import RateLimiter
from src.conf.config import settings
from src.conf.transformation import TRANSFORMATIONS
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.transformation import PhotoResponse, UrlResponse
from src.database.db import get_db
from src.repository import transformation as ts
from src.entity.models import User
from src.services.auth import auth_service
from src.repository import posts as repository_posts
from src.schemas.post import PostModel, PostResponse, PostDeletedResponse


router = APIRouter(prefix="/transformation", tags=["transformation"])
cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

async def url_qr_prefix(list_tr):
    """
    Creates a string from the incoming transformation parameter sheet for a Qrcode URL prefix.

    :param list_tr: Transformation Parameters Sheet.
    :type list_tr: str
    :return: A line of params.
    :rtype: str
    """
    prefix = ""
    for i in list_tr:
        if i != None:
            prefix += i
    return prefix

async def create_qr(url_transform):
    """
    Creates a Qrcode image with a link to a photo.

    :param url_transform: Link to photo.
    :type url_transform: str
    :return: Byte string Qrcode.
    :rtype: class 'bytes'
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
    Checks connection with the Cloudinary service, if successful, returns the status "Ok".

    :return: A dict of connection status.
    :rtype: dict
    """
    ping = cloudinary.api.ping()
    print(ping)
    return ping


@router.get("/info_all_transformation",dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def info_all_transformation():
    """   
    Creates a request to obtain data about available transformations.

    :return: A dict of transformations.
    :rtype: dict
    """
    return TRANSFORMATIONS


@router.post("/transformation_photo",dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def transformation_photo(
        id: int ,
        create_qrcode: bool ,
        transformation_1: str ,
        transformation_2: str | None = None,
        transformation_3: str | None = None,
        transformation_4: str | None = None,
        transformation_5: str | None = None,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)):
    """
    
    Creates a link with transformation parameters for the Cloudinary service.
    The id field is used to enter the post id.
    The create_qrcode field is used to create a qrcode for a link; to create a link you must set it to True.
    The transformation availability is entered into the transformation fields.
    For example: crop , rotate , effect , overlays , vignette , face , pixelate_faces , cartoonify, opacity.

    :param id: Post number with photo for transformation.
    :type id: int
    :param create_qrcode: Boolean value to create Qrcode.
    :type create_qrcode: bool
    :param transformation_1: Transformation parameter.
    :type transformation_1: str
    :param transformation_2: Transformation parameter.
    :type transformation_2: str
    :param transformation_3: Transformation parameter.
    :type transformation_3: str
    :param transformation_4: Transformation parameter.
    :type transformation_4: str
    :param transformation_5: Transformation parameter.
    :type transformation_5: str
    :param db: The database session.
    :type db: Session
    :param user: The user to retrieve post for.
    :type user: User
    :return: A list of image link sheet
    :rtype: list
    """
    info_photo = await ts.get_photo_info(id, user, db)
    if info_photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    list_tr = [transformation_1,transformation_2,transformation_3,transformation_4,transformation_5]
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
    url_transform = cloudinary.CloudinaryImage(public_id).build_url(transformation =
        [
            TRANSFORMATIONS.get(transformation_1),
            TRANSFORMATIONS.get(transformation_2),
            TRANSFORMATIONS.get(transformation_3),
            TRANSFORMATIONS.get(transformation_4),
            TRANSFORMATIONS.get(transformation_5),
            ])

    prefix = url_qr_prefix(list_tr)
    url_qr = None
    publick_url_qr = None
    if create_qrcode == True:
        img = await create_qr(url_transform)       
        prefix = await url_qr_prefix(list_tr)
        publick_url_qr = f"{public_id}_{prefix}_qr"
        result = cloudinary.uploader.upload(img, public_id=publick_url_qr, owerite=True)
        url_qr = cloudinary.CloudinaryImage(publick_url_qr).build_url(version=result.get("version"))
    await ts.update_qr(id , url_transform,  url_qr, publick_url_qr, db)
    return url_origin , url_transform , url_qr


@router.get("/show_photo_url",response_model=PhotoResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def show_photo_url(id: int, user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Creates a database query to obtain information about a photo links of a registered user.

    :param id: Post number with photo for transformation.
    :type id: int
    :param db: The database session.
    :type db: Session
    :param user: The user to retrieve post for.
    :type user: User
    :return: Links to transform photos
    :rtype: PhotoResponse
    """
    result = await ts.get_photo_url( id, user, db)
    #json_formatted_str = json.dumps(result, indent=2)
    #print(f"_______________________________{result.all_images}_________________________")
    #for i in 
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result

@router.get("/show_all_url",response_model=List[PhotoResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def show_all_url(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Creates a database query to obtain information about all photo links of a registered user.

    :param offset: The number of contacts to skip.
    :type offset: int
    :param limit: The maximum number of cntacts to return.
    :type limit: int
    :param user: The user to retrieve post for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: Links to transform photos
    :rtype: List[PhotoResponse]
    """
    result = await ts.get_all_url(limit,offset, user, db)

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
