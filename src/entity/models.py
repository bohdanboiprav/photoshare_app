from datetime import date
from sqlalchemy import String, types, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase
import uuid


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(150), unique=True)
    password: Mapped[str] = mapped_column(String(500))
    avatar: Mapped[str] = mapped_column(String(255))
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime(timezone=True),
                                             default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime(timezone=True),
                                             default=func.now(), onupdate=func.now(), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    user_type_id: Mapped[int] = mapped_column(ForeignKey('user_type.id'))
    user_type: Mapped["UserType"] = relationship("UserType", backref="users", lazy="joined")


class UserType(Base):
    __tablename__ = 'user_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), default=1)
