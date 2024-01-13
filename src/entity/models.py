from datetime import date
from sqlalchemy import String, Date, Integer, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime(timezone=True),
                                             default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime(timezone=True),
                                             default=func.now(), onupdate=func.now(), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    user_type_id: Mapped[int] = mapped_column(ForeignKey('user_type.id'), nullable=True)


class UserType(Base):
    __tablename__ = 'user_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), default=1)
