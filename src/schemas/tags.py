from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, validator


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagUpdate(TagModel):
    tags: Optional[List[str]] = Field(max_length=25, default=None)

    @validator("tags")
    def validate_tags(cls, value):
        if len(value) > 5:
            raise ValueError("Number of tags cannot be more than 5.")
        return value


class TagResponse(TagModel):
    id: int
    name: str

    ConfigDict(from_attributes=True)
