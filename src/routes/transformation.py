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
    prefix = ""
    for i in list_tr:
        if i != None:
            prefix += i
    return prefix


async def create_qr(url_transform):
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
    ping = cloudinary.api.ping()
    print(ping)
    return ping


@router.get("/info_all_transformation", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def info_all_transformation():
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
    result = await ts.get_photo_url(id, user, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result


@router.post("/show_all_url", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def show_all_url(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await ts.get_all_url(limit, offset, user, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return result
