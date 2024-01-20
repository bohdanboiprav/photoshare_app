from types import NoneType

import cloudinary
import cloudinary.uploader

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    status, Path
)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter
from src.conf import messages
from src.database.db import get_db
from src.entity.models import User
from src.repository.users import get_user_by_username, get_user_by_email
from src.schemas.user import UserResponse, UserSchema, UserProfileResponse
from src.services.auth import auth_service
from src.conf.config import settings
from src.repository import users as repository_users
from src.repository import profile as repository_profile

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Specify the type of object that is returned by the auth_service
    :return: The current user, which is stored in the database
    :doc-author: Trelent
    """
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def get_current_user(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It takes in an UploadFile object, which is a file
        uploaded by the user, and uses it to update their avatar URL on Cloudinary.

    :param file: UploadFile: Get the file from the request
    :param user: User: Get the current user
    :param db: AsyncSession: Get the database connection
    :param : Get the current user
    :return: The current user
    :doc-author: Trelent
    """
    public_id = f"Photoshare_app/Avatars/{user.id}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(res["public_id"]).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repository_users.update_avatar_url(user.email, res_url, db)
    return user


@router.get("/{username}/profile/", status_code=status.HTTP_200_OK)
async def get_user_profile(
        username: str = Path(),
        db: AsyncSession = Depends(get_db),
):
    user = await repository_users.get_user_by_username(username, db)
    if user:
        result = await repository_profile.get_profile(user, db)
        return result
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND
    )


@router.put("/{username}/profile/update", response_model=UserResponse,
            dependencies=[Depends(RateLimiter(times=1, seconds=30))],
            status_code=status.HTTP_200_OK)
async def update_user_profile(body: UserSchema, db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(auth_service.get_current_user)):
    body.password = auth_service.get_password_hash(body.password)

    if (current_user.email == body.email) and (current_user.username != body.username):
        exist_user = await get_user_by_username(body.username, db)
        if exist_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=messages.USER_EXIST
            )

    elif (current_user.username == body.username) and (current_user.email != body.email):
        exist_user = await get_user_by_email(body.email, db)
        if exist_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=messages.EMAIL_EXIST
            )
    user = await repository_profile.update_user_profile(body, current_user, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return user


@router.post("/ban_user/{username}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def request_email(username: str = Path(),
                        current_user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_db)):
    if current_user.user_type_id == 3:
        banned_user = await repository_users.ban_user(username, db)
        return banned_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
