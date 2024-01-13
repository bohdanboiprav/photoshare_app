import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict, UUID4


class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)
    avatar: str = Field(max_length=255)


class UserTypeResponse(BaseModel):
    id: int
    user: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: UUID4
    username: str
    email: EmailStr
    avatar: str
    created_at: datetime
    updated_at: datetime
    confirmed: bool
    user_type: UserTypeResponse

    model_config = ConfigDict(from_attributes=True)


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
