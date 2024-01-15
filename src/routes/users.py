from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas.user import UserModel, UserResponse

# from src.services.auth import auth_service

router = APIRouter(prefix='/users', tags=["users"])

#upd

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(body: UserModel, db: AsyncSession = Depends(get_db)):
    new_user = await repository_users.create_user(body, db)
    return new_user


@router.get("/getuser", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    new_user = await repository_users.get_user(username, db)
    return new_user
