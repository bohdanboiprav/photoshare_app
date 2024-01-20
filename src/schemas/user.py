import uuid
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserSchema(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    avatar: str
    model_config = ConfigDict(from_attributes=True)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr


class UpdateProfile(BaseModel):
    username: str | None = Field()
