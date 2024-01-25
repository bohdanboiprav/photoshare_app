import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from src.conf import messages
from src.conf.cloudinary import configure_cloudinary
from src.database.db import get_db
from src.entity.models import User
from src.schemas.post import PostModel, PostResponse, PostDeletedResponse
from src.repository import posts as repository_posts
from src.schemas.tag import TagUpdate
from src.services.auth import auth_service

router = APIRouter(prefix='/posts', tags=["posts"])


@router.get("/", response_model=List[PostResponse])
async def get_posts(current_user: User = Depends(auth_service.get_current_user),
                    db: AsyncSession = Depends(get_db)):
    """
    The get_posts function returns a list of posts.

    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: All posts in the database
    """
    post = await repository_posts.get_posts(db)
    return post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int = Path(ge=1),
                   current_user: User = Depends(auth_service.get_current_user),
                   db: AsyncSession = Depends(get_db)):
    """
    The get_post function is used to retrieve a single post from the database.
    It takes an integer as its only argument, which represents the ID of the post
    to be retrieved. It returns a Post object if successful.

    :param post_id: int: Specify the type of the parameter, and it is also used to specify that
    :param current_user: User: Get the current user from the auth_service
    :param db: AsyncSession: Get a database connection
    :return: A post object
    """
    post = await repository_posts.get_post(post_id, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post is not found")
    return post


def checker(data: str = Form(...)):
    """
    The checker function is a custom validator that will be used to validate the
    JSON data sent in the request body. It uses FastAPI's Form() parameter type, which
    will automatically parse and deserialize JSON into Python objects. The checker function
    then passes this data to PostModel's model_validate_json method, which will raise a
    ValidationError if any of the fields fail validation.

    :param data: str: Get the json data from the request body
    :return: A dict with the validated data
    """
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
                      current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_db)):
    configure_cloudinary()
    """
    The create_post function creates a new post in the database.
        It takes in a PostModel object, an UploadFile object, and the current_user as arguments.
        The function then uploads the file to cloudinary using their API and returns an image url for that file.
        The function then calls create_post from repository_posts which adds all of this information to our database.

    :param body: PostModel: Get the body of the post from the request
    :param file: UploadFile: Upload the file to cloudinary
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A postmodel object
    """
    unique_path = uuid.uuid4()
    r = cloudinary.uploader.upload(file.file, public_id=f'Photoshare_app/{current_user.username}/{unique_path}')
    image_url = cloudinary.CloudinaryImage(f'Photoshare_app/{current_user.username}/{unique_path}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    image_id = f'Photoshare_app/{current_user.username}/{unique_path}'
    return await repository_posts.create_post(body, image_url, image_id, current_user, db)


@router.post("/add_tags", response_model=PostResponse)
async def add_tags_to_post(body: TagUpdate, user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_db)):
    """
    The add_tags_to_post function adds tags to a post.
        The function takes in the body of the request, which contains an array of tag ids and a post id.
        It also takes in user information from auth_service and database connection information from get_db().

    :param body: TagUpdate: Get the tag_id from the request body
    :param user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A post object
    """
    if user.user_type_id in [2, 3]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tags can be added only by users")
    post = await repository_posts.add_tag_to_post(body, user, db)
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(body: PostModel, post_id: int = Path(ge=1),
                      current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_db)):
    """
    The update_post function updates a post in the database.
        It takes an id of the post to update, and a body containing new values for that post.
        The user must be logged in to use this function.

    :param body: PostModel: Get the data from the request body
    :param post_id: int: Get the post id from the path
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: A postmodel object
    """
    post = await repository_posts.update_post(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND)
    return post


@router.delete("/{post_id}", response_model=PostDeletedResponse)
async def remove_post(post_id: int = Path(ge=1),
                      current_user: User = Depends(auth_service.get_current_user),
                      db: AsyncSession = Depends(get_db)):
    """
    The remove_post function removes a post from the database.

    :param post_id: int: Specify the post id
    :param current_user: User: Get the current user
    :param db: AsyncSession: Get the database session
    :return: The removed post
    """
    post = await repository_posts.remove_post(post_id, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=messages.POST_NOT_FOUND)
    return post
