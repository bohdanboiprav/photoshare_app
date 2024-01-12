from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, PastDate, ConfigDict
from src.schemas.user import UserResponse


class PostModel(BaseModel):
    name: str = Field(max_length=70)
    surname: str = Field(max_length=70)
    email: EmailStr = Field()
    phone: str = Field(max_length=50)
    date_of_birth: PastDate = Field()
    additional_info: Optional[str] = Field(max_length=300)


class PostResponse(BaseModel):
    id: int
    name: str = Field(max_length=70)
    surname: str = Field(max_length=70)
    email: EmailStr = Field()
    phone: str = Field(max_length=50)
    date_of_birth: date
    additional_info: Optional[str] = Field(max_length=300)
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)
