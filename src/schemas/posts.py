from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, validator

from src.schemas.tags import TagModel


class PostModel(BaseModel):
    name: str = Field(max_length=2000)
    content: str = Field(max_length=5000)
    image: str = Field(max_length=255)
    user_id: str | None = Field(max_length=20, default=None)
    tags: Optional[List[str]] = Field(max_length=5, default=None)

    @validator("tags")
    def validate_tags(cls, value):
        if len(value) > 5:
            raise ValueError("Number of tags cannot be more than 5.")
        return value


class PostResponse(BaseModel):
    name: str
    content: str
    image: str | None
    user_id: str | None
    tags: List[TagModel] | None

    ConfigDict(from_attributes=True)


