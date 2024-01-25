from typing import List, Optional, Dict

from pydantic import BaseModel, Field, ConfigDict, validator, field_validator, ConfigDict
from src.entity.models import PhotoUrl


class UrlResponse(BaseModel):
    transform_url: str | None
    transform_url_qr: str | None


class PhotoResponse(BaseModel):
    name: str
    image: str
    user: UrlResponse
    url: List[UrlResponse] | None

    # model_config = ConfigDict(from_attributes=True)
