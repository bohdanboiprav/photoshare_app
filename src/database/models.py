import uuid
from datetime import date
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, func, DateTime, Enum, Integer, ForeignKey, Boolean, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class UserType(Base):
    __tablename__ = 'user_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(String(50), nullable=False)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(500), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    user_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_type.id'), nullable=False)


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(String(5000))
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[uuid] = mapped_column(UUID, ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", backref="posts", lazy="joined")
    tags_to_posts: Mapped[List["TagToPost"]] = relationship("TagToPost", backref="post", lazy="joined")


class Tag(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    tags_to_posts: Mapped[List["TagToPost"]] = relationship("TagToPost", backref="tag", lazy="joined")


class TagToPost(Base):
    __tablename__ = 'tags_to_posts'
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), nullable=False)
    post: Mapped["Post"] = relationship("Post", backref="tags_to_posts", lazy="joined")
    tag: Mapped["Tag"] = relationship("Tag", backref="tags_to_posts", lazy="joined")
