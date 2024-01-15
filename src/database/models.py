import uuid
from datetime import date
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, func, DateTime, Enum, Integer, ForeignKey, Boolean, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass