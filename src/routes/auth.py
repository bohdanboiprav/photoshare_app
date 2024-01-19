from src.conf import messages
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
    Response,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email


router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserSchema,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The signup function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param bt: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base_url of the application
    :param db: AsyncSession: Pass the database session to the repository function
    :param : Get the user's email and username to send an email
    :return: A user object
    :doc-author: Trelent
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    The login function is used to authenticate a user.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Get the database session from the dependency
    :return: A jwt, which is a json object with the following keys:
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_INVALID_EMAIL
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.NOT_CONFIRMED_EMAIL,
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_INVALID_PASSWORD
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
    It takes a refresh token as input and returns an access token.
    The function first decodes the refresh_token to get the user's email address, then it gets that user from our database,
    and checks if their stored refresh_token matches what was sent in with this request. If not, we raise an error and return a 401 Unauthorized response code (the client will need to log in again).
    If everything checks out, we create new tokens for this user using our auth service module and update their record in our database with these new tokens.

    :param credentials: HTTPAuthorizationCredentials: Get the access token from the request header
    :param db: AsyncSession: Pass the database session to the function
    :param : Get the user from the database
    :return: A new access token and refresh token
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.AUTH_INVALID_REFRESH_TOKEN
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.

    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database session
    :return: A message if the email is already confirmed or a different one if it is not
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=messages.AUTH_VERIFICATION_ERROR
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The request_email function is used to send an email to the user with a link that they can click on
    to confirm their email address. The function takes in a RequestEmail object, which contains the
    email of the user who wants to confirm their account. It then checks if there is already a confirmed
    user with that email address, and if so returns an error message saying as much. If not, it sends them
    an email containing a link they can click on to confirm their account.

    :param body: RequestEmail: Validate the request body against
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base url of our application
    :param db: AsyncSession: Get the database session
    :param : Get the user's email from the database
    :return: A message to the user
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Check your email for confirmation."}


@router.post("/reset_password")
async def reset_password(
    body: RequestEmail,
    bt: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    The reset_password function is used to reset a user's password.

    :param body: RequestEmail: Get the email from the request body
    :param bt: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: AsyncSession: Get the database session
    :param : Get the user id from the token
    :return: A message
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.AUTH_ALREADY_EXISTS
        )
    bt.add_task(
        send_email,
        user.email,
        user.username,
        str(request.base_url),
        type="reset_password",
    )
    return {"message": messages.AUTH_CHECK_EMAIL}


@router.get("/confirmed_reset_password/{token}")
async def confirmed_reset_password(
    token: str, password1: str, password2: str, db: AsyncSession = Depends(get_db)
):
    """
    The confirmed_reset_password function is used to reset a user's password.
    It takes in the token, password 1 and 2 as parameters. It then checks if the passwords are equal,
    if not it raises an HTTPException with status code 400 and detail &quot;Your passwords are not the same&quot;.
    If they are equal it gets the email from token using auth_service.get_email_from_token(token).
    Then it gets user by email using repository users get user by email function (repository users get
    user by email returns a User object). Then we set that User objects password to be what was passed in


    :param token: str: Get the email from the token
    :param password1: str: Get the new password from the user
    :param password2: str: Make sure that the user entered the same password twice
    :param db: AsyncSession: Get the database session
    :return: A dictionary with a message
    :doc-author: Trelent
    """
    if password1 != password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.AUTH_PASSWORD_NOT_SAME,
        )
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    user.password = auth_service.get_password_hash(password1)
    await repository_users.confirmed_email(email, db)
    return {"message": "Your password changed"}

