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
from src.conf.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/photo_url_qr", tags=["photo_url_qr"])
cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get(
    "/ping_cloudinary",
)
async def get_photos_info():
    """
    The get_photos_info function returns a dictionary of information about the photos in the Cloudinary account.
        The function is called by the /photos_info route, which is accessed via an HTTP GET request.

    :return: A dictionary with the following keys:
    :doc-author: Trelent
    """
    ping = cloudinary.api.ping()
    return ping


@router.get(
    "/info_all_photo",
)
async def get_photos_info():
    """
    The get_photos_info function returns a list of dictionaries containing information about the photos in the Cloudinary account.
    The function uses the resources() method from Cloudinary's Python SDK to return a dictionary with all of this information.

    :return: A dictionary of all the photos in your cloudinary account
    :doc-author: Trelent
    """
    resources = cloudinary.api.resources()
    return resources


# test/tesmail@i.ua
@router.post(
    "/photo_url_qr/{public_id}",
)
async def get_url_photo(public_id: str):
    """
    The get_url_photo function takes a public_id as an argument and returns the url of the photo with that public_id.
        Args:
            public_id (str): The unique identifier for a photo in Cloudinary.

    :param public_id: str: Specify the name of the image in cloudinary
    :return: A tuple with two values
    :doc-author: Trelent
    """
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

