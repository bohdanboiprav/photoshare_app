import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Post, User
from src.schemas.post import PostModel
