from datetime import datetime
from typing import Optional, List

import uuid

from src.schemas.post import PostResponse
from src.schemas.user import UserResponse
from pydantic import BaseModel


class CommentModel(BaseModel):
    content: str
    post_id: int


class CommentResponse(BaseModel):
    id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    post: PostResponse
