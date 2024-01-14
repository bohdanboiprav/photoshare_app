from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, PastDate, ConfigDict

from src.schemas.user import UserResponse


# from src.schemas.user import UserResponse


class PostModel(BaseModel):
    name: str | None = Field(max_length=200)
    content: str | None = Field(max_length=5000)


class PostResponse(BaseModel):
    id: int
    name: str = Field(max_length=200)
    content: str = Field(max_length=5000)
    created_at: datetime
    updated_at: datetime
    image: str = Field(max_length=255)
    user: UserResponse
    tags: list

    model_config = ConfigDict(from_attributes=True)