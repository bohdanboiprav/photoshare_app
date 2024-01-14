from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, PastDate, ConfigDict, field_validator

from src.schemas.tag import TagModel
from src.schemas.user import UserResponse


# from src.schemas.user import UserResponse


class PostModel(BaseModel):
    name: str | None = Field(max_length=200)
    content: str | None = Field(max_length=5000)
    tags: Optional[List[str]] = Field(max_length=5, default=None)

    @field_validator("tags")
    def validate_tags(cls, value):
        if len(value) > 5:
            raise ValueError("Number of tags cannot be more than 5.")
        return value


class PostResponse(BaseModel):
    id: int
    name: str = Field(max_length=200)
    content: str = Field(max_length=5000)
    created_at: datetime
    updated_at: datetime
    image: str = Field(max_length=255)
    user: UserResponse
    tags: List[TagModel] | None

    model_config = ConfigDict(from_attributes=True)
