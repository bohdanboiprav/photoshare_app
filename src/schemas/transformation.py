from typing import List, Optional ,Dict

from pydantic import BaseModel, Field, ConfigDict, validator, field_validator,ConfigDict
from src.entity.models import PhotoUrl


class UrlResponse (BaseModel):
    transform_url: str | None 
    transform_url_qr: str | None


class PhotoResponse(BaseModel):
    name: str | None
    image_url: str | None
    all_images: List[UrlResponse] | None


    

