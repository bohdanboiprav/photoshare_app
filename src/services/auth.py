import pickle
from datetime import datetime, timedelta
from typing import Optional

import redis
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings
from src.conf import messages


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.SECRET_KEY_JWT
    ALGORITHM = settings.ALGORITHM
    cache = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        password=settings.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Make the method belong to the class
        :param plain_password: Pass in the password that is entered by the user
        :param hashed_password: Compare the hashed password stored in the database to the plain text password that is entered by a user
        :return: A boolean value
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Represent the instance of the class
        :param password: str: Pass in the password that we want to hash
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    # define a function to generate a new access token
    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_access_token function creates a new access token.
            Args:
                - data (dict): A dictionary containing the claims to be encoded in the JWT.
                - expires_delta (Optional[float]): An optional parameter specifying how long, in seconds,
                the access token should last before expiring. If not specified, it defaults to 15 minutes.

        :param self: Make the function a method of the class
        :param data: dict: Pass the data that will be encoded into the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: An encoded access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                - data (dict): A dictionary containing the user's id and username.
                - expires_delta (Optional[float]): The time in seconds until the token expires. Defaults to None, which sets it to 7 days from now.

        :param self: Represent the instance of the class
        :param data: dict: Pass in the data that will be encoded into the token
        :param expires_delta: Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.AUTH_NOT_VALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
        """
        The decode_refresh_token function is used to decode the refresh token.
        It will raise an exception if the token is invalid or has expired.
        If it's valid, it returns the email address of the user.

        :param self: Represent the instance of a class
        :param refresh_token: str: Pass in the refresh token that is being decoded
        :return: The email of the user who is trying to refresh their access token
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            print(payload)
            if payload["scope"] == "refresh_token":
                email = payload["sub"]

                is_blocked = self.cache.get(str(email) + "_blacklist_refresh")
                if is_blocked is not None and is_blocked.decode('utf-8') == refresh_token:
                    raise credentials_exception

                return email

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.AUTH_NOT_VALID_CREDENTIALS,
            )

    async def get_current_user(
            self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
    ):
        """
        The get_current_user function is a dependency that will be used in the
            protected endpoints. It takes a token as an argument and returns the user
            object if it exists, otherwise it raises an exception.

        :param self: Access the class variables
        :param token: str: Get the token from the authorization header
        :param db: AsyncSession: Pass the database session to the function
        :return: A user object
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.AUTH_NOT_VALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)

        # Check if the user is in the blacklist
        is_blocked = self.cache.get(user_hash + "_blacklist_access")
        if is_blocked is not None and is_blocked.decode('utf-8') == token:
            raise credentials_exception

        user = self.cache.get(user_hash)

        if user is None:
            print(messages.AUTH_USER_NOT_IN_CACHE)
            user = await repository_users.get_user_by_email(email, db)
            if user is None or user.is_banned:
                raise credentials_exception

            # Check if user's refresh token is in the blacklist
            if user.refresh_token is not None:
                refresh_token_blocked = self.cache.get(user.refresh_token + "_blacklist_refresh")
                if refresh_token_blocked is not None:
                    raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print(messages.AUTH_USER_IN_CACHE)
            user = pickle.loads(user)

        return user

    def create_email_token(self, data: dict):
        """
        The create_email_token function takes a dictionary of data and returns a token.
        The token is created by encoding the data with the SECRET_KEY and ALGORITHM,
        and adding an iat (issued at) timestamp and exp (expiration) timestamp to it.

        :param self: Make the function a method of the class
        :param data: dict: Encode the token
        :return: A token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        The function uses PyJWT to decode the token, which is then used to retrieve the email address from its payload.

        :param self: Represent the instance of the class
        :param token: str: Store the token that is passed in from the route
        :return: The email address of the user who is trying to verify their account
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=messages.AUTH_INVALID_TOKEN,
            )


auth_service = Auth()
