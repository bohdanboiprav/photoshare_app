import datetime
from typing import List, Optional

import uuid
from pydantic import BaseModel, Field, ConfigDict, validator, field_validator

from src.entity.models import Post
from src.schemas.post import PostResponse
from src.schemas.user import UserResponse


class RateModel(BaseModel):
    value: int
    post_id: int

    @field_validator("value")
    def validate_tags(cls, value):
        if value not in range(1, 6):
            raise ValueError("Value should be between 1 and 5")
        return value


class RateResponse(BaseModel):
    value: int
    user: UserResponse
    post: PostResponse

    model_config = ConfigDict(from_attributes=True)