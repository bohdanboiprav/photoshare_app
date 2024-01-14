import uuid

from fastapi import APIRouter, HTTPException, Depends, status, Path, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from src.conf.config import settings
from src.database.db import get_db
from src.repository.users import get_user
from src.schemas.post import PostModel, PostResponse
from src.repository import posts as repository_posts

# from src.services.auth import auth_service

router = APIRouter(prefix='/posts', tags=["posts"])


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int = Path(ge=1),
                   db: AsyncSession = Depends(get_db)):
    new_user = await get_user("string", db)
    post = await repository_posts.get_post(post_id, new_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post


@router.post("/create")
async def create_post(body: PostModel = Depends(), file: UploadFile = File(),
                      db: AsyncSession = Depends(get_db)):
    new_user = await get_user("string", db)
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    unuque_path = uuid.uuid4()
    r = cloudinary.uploader.upload(file.file, public_id=f'Photoshare_app/{new_user.username}/{unuque_path}')
    src_url = cloudinary.CloudinaryImage(f'Photoshare_app/{new_user.username}/{unuque_path}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    return await repository_posts.create_post(body, src_url, new_user, db)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(body: PostModel, post_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db)):
    new_user = await get_user("string", db)
    post = await repository_posts.update_post(post_id, body, new_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post


# @router.put("/update/{post_id}", response_model=PostResponse)
# async def update_photo(file: UploadFile = File(), post_id: int = Path(ge=1),
#                        db: AsyncSession = Depends(get_db)):
#     new_user = await get_user("string", db)
#     cloudinary.config(
#         cloud_name=settings.CLOUDINARY_NAME,
#         api_key=settings.CLOUDINARY_API_KEY,
#         api_secret=settings.CLOUDINARY_API_SECRET,
#         secure=True
#     )
#     r = cloudinary.uploader.upload(file.file, public_id=f'Photoshare_app/{new_user.username}', overwrite=True)
#     src_url = cloudinary.CloudinaryImage(f'Photoshare_app/{new_user.username}') \
#         .build_url(width=250, height=250, crop='fill', version=r.get('version'))
#     post = await repository_posts.get_post(post_id, new_user, db)
#     post.image = src_url
#     await db.commit()
#     await db.refresh(post)
#     if post is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
#     return post


@router.delete("/{post_id}", response_model=PostResponse)
async def remove_post(post_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db)):
    new_user = await get_user("string", db)
    post = await repository_posts.remove_post(post_id, new_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post
