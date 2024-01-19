from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, PastDate, ConfigDict, field_validator

from src.schemas.tag import TagModel, TagResponse
from src.schemas.user import UserResponse


# from src.schemas.user import UserResponse


class PostModel(BaseModel):
    name: str | None = Field(max_length=50)
    content: str | None = Field(max_length=5000)
    tags: Optional[List[str]] = Field(max_length=5, default=None)

    @field_validator("tags")
    def validate_tags(cls, value):
        if len(value) > 5:
            raise ValueError("Number of tags cannot be more than 5.")
        return value


class PostDeletedResponse(BaseModel):
    id: int
    name: str


class PostResponse(BaseModel):
    id: int
    name: str
    content: str
    created_at: datetime
    updated_at: datetime
    image: str
    user: UserResponse
    tags: List[TagResponse] | None

    model_config = ConfigDict(from_attributes=True)

