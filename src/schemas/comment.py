from datetime import datetime
from typing import Optional, List

import uuid

from src.schemas.post import PostResponse
from src.schemas.user import UserResponse
from pydantic import BaseModel, ConfigDict


class CreateCommentModel(BaseModel):
    content: str
    post_id: int


class CommentUpdateModel(BaseModel):
    content: str
    comment_id: uuid.UUID


class CommentDeleteModel(BaseModel):
    comment_id: uuid.UUID


class CommentResponse(BaseModel):
    id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    post: PostResponse


class CommentResponse(BaseModel):
    id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    post: PostResponse

    model_config = ConfigDict(from_attributes=True)


# user@example.com
# string1
#
# admin@admin.com
# admin123