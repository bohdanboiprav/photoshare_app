from typing import List
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import ValidationError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
<<<<<<< Updated upstream
from src.repository import posts as repository_posts
from src.schemas.posts import PostModel, PostResponse
from src.schemas.tags import TagResponse, TagUpdate
=======
from src.entity.models import User
from src.repository.users import get_user_by_email
from src.schemas.post import PostModel, PostResponse
from src.repository import posts as repository_posts
from src.schemas.tag import TagUpdate, TagResponse
from src.services.auth import auth_service
>>>>>>> Stashed changes

router = APIRouter(prefix="/posts", tags=["posts"])


<<<<<<< Updated upstream
@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostModel,
    db: AsyncSession = Depends(get_db),
):
    post = await repository_posts.create_post(body, db)
    return post


@router.post("/add", response_model=TagResponse)
async def add_tags_to_post(body: TagUpdate, db: AsyncSession = Depends(get_db)):
    tag = await repository_posts.add_tag_to_post(body, db)
    return tag

=======
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int = Path(ge=1),
                   db: AsyncSession = Depends(get_db)):
    new_user = await get_user_by_email("dimalikegtr@gmail.com", db)
    post = await repository_posts.get_post(post_id, new_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post


def checker(data: str = Form(...)):
    try:
        return PostModel.model_validate_json(data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


test = {"name": "string2", "content": "string", "tags": ["string1", "string2"]}


@router.post("/create", response_model=PostResponse)
async def create_post(body: PostModel = Depends(checker), file: UploadFile = File(),
                      db: AsyncSession = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    unique_path = uuid.uuid4()
    r = cloudinary.uploader.upload(file.file, public_id=f'Photoshare_app/{current_user.username}/{unique_path}')
    src_url = cloudinary.CloudinaryImage(f'Photoshare_app/{current_user.username}/{unique_path}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    return await repository_posts.create_post(body, src_url, current_user, db)


@router.post("/add_tags", response_model=PostResponse)
async def add_tags_to_post(body: TagUpdate, user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    if user.user_type_id in [2, 3]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tags can be added only by users")
    post = await repository_posts.add_tag_to_post(body, user, db)
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(body: PostModel, post_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db)):
    new_user = await get_user_by_email("string", db)
    post = await repository_posts.update_post(post_id, body, new_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post


@router.delete("/{post_id}", response_model=PostResponse)
async def remove_post(post_id: int = Path(ge=1),
                      db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    post = await repository_posts.remove_post(post_id, user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post
>>>>>>> Stashed changes
