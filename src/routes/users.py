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
from src.conf.cloudinary import configure_cloudinary
from src.database.db import get_db
from src.entity.models import User
from src.repository.users import get_user_by_username, get_user_by_email
from src.schemas.user import UserResponse, UserSchema, UserProfileResponse, UserRight
from src.services.auth import auth_service
from src.repository import users as repository_users
from src.repository import profile as repository_profile

router = APIRouter(prefix="/users", tags=["users"])
configure_cloudinary()


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
    :return: The current user
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
    """
    The get_user_profile function is a GET request that returns the profile of a user. The username parameter is
    required and must be unique. The db parameter uses the get_db function to connect to the database.

    :param username: str: Get the username from the path
    :param db: AsyncSession: Pass the database session to the function
    :return: A dict with the user's profile information
    """
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
    """
    The update_user_profile function updates a user's profile.
        Args:
            - body (UserSchema): The UserSchema object containing the new data for the user.
            - db (AsyncSession, optional): [description]. Defaults to Depends(get_db).
            - current_user (User, optional): [description]. Defaults to Depends(auth_service.get_current_user).

    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the connection to the database
    :param current_user: User: Get the current user
    :return: A user object
    """
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
async def ban_user(username: str = Path(),
                   current_user: User = Depends(auth_service.get_current_user),
                   db: AsyncSession = Depends(get_db)):
    """
    The ban_user function is used to ban a user.
        The function takes in the username of the user that needs to be banned and returns a boolean value indicating if
        the operation was successful or not.

    :param username: str: Get the username of the user that is to be banned
    :param current_user: User: Get the current user
    :param db: AsyncSession: Create a database session
    :return: A user object
    """
    if current_user.user_type_id == 3:
        banned_user = await repository_users.ban_user(username, db)
        if banned_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
        return banned_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("/unban_user/{username}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def unban_user(username: str = Path(),
                     current_user: User = Depends(auth_service.get_current_user),
                     db: AsyncSession = Depends(get_db)):
    """
    The unban_user function is used to unban a user.
        The function takes in the username of the user that needs to be unbanned, and returns a message confirming that
        the user has been unbanned.

    :param username: str: Get the username of the user that is to be banned
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: The unbanned user object
    :doc-author: Trelent
    """
    if current_user.user_type_id == 3:
        unbanned_user = await repository_users.unban_user(username, db)
        if unbanned_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
        return unbanned_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("/assign_role/{username}", status_code=status.HTTP_200_OK, response_model=UserRight)
async def assign_role(role_type: str,
                      username: str = Path(),
                      current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_db)):

    """
    The assign_role function is used to assign a role to a user.
        The function takes in the following parameters:
            - role_type: A string representing the type of role that will be assigned.
                This can either be &quot;User&quot;, &quot;Moderator&quot; or &quot;Admin&quot;. If any other value is passed, an error will be raised.

    :param role_type: str: Specify the role type to be assigned
    :param username: str: Get the username of the user to be deleted
    :param current_user: User: Get the current user's information
    :param db: AsyncSession: Get the database session
    :return: A user object
    :doc-author: Trelent
    """
    if role_type not in ("User", "Moderator", "Admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.INVALID_ROLE_TYPE)
    if current_user.user_type_id == 3:
        user = await repository_users.assign_role(username, role_type, db)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.USER_NOT_FOUND)
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
