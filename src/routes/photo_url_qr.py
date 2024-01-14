import pickle
import io
from PIL import Image, ImageDraw

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
    Path,
    Query,
    UploadFile,
    File,
)
from src.conf.config import config
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/photo_url_qr", tags=["photo_url_qr"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/ping_cloudinary",
)
async def get_photos_info():
    ping = cloudinary.api.ping()
    return ping


@router.get(
    "/info_all_photo",
)
async def get_photos_info():
    resources = cloudinary.api.resources()
    return resources


# test/tesmail@i.ua
@router.post(
    "/photo_url_qr/{public_id}",
)
async def get_url_photo(public_id: str):
    folder = "test"
    print(public_id)
    result_all_info = cloudinary.api.resource(F"{folder}/{public_id}")
    result_url = result_all_info.get('secure_url')
    

    qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=4,
    )
    qr.add_data(result_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format=img.format)
    imgByteArr = imgByteArr.getvalue()
    public_id_qr = f"test/tesmail@i.ua.qr"
    res = cloudinary.uploader.upload(imgByteArr, public_id=public_id_qr, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id_qr).build_url(version=res.get("version"))
    #json_ = json.dumps(result_all_info, indent=2)
    return result_url , res_url

