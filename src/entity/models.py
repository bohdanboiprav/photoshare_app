import uuid
from datetime import date
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates, registry
from sqlalchemy import String, Date, func, DateTime, Enum, Integer, ForeignKey, Boolean, UUID, Table, Column
from sqlalchemy.orm import DeclarativeBase

mapper_registry = registry()


class Base(DeclarativeBase):
    pass


class UserType(Base):
    __tablename__ = 'user_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column(String(50), nullable=False)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(500), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    user_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('user_type.id'), nullable=False)
    user_type: Mapped["UserType"] = relationship("UserType", backref="users", lazy="joined")


# association_table = Table(
#     "tags_to_posts",
#     Base.metadata,
#     Column("post_id", ForeignKey("posts.id")),
#     Column("tag_id", ForeignKey("tags.id")),
# )

# class Association(Base):
#     __tablename__ = "tags_to_posts"
#     # id: Mapped[int] = mapped_column(primary_key=True)
#     post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
#     tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
#     child: Mapped["Tag"] = relationship()


class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(String(5000), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[uuid] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    user: Mapped["User"] = relationship("User", backref="posts", lazy="joined")
    # tags: Mapped[List["Association"]] = relationship(lazy="joined")
    # tags: Mapped[List["Tag"]] = relationship(secondary=association_table)
    # tags: Mapped[List["Tag"]] = relationship("TagToPost", backref="post", lazy="selectin")

    tags: Mapped[List["Tag"]] = relationship("Tag", secondary="tags_to_posts", back_populates="posts", lazy="joined")
    tags_to_posts: Mapped[List["TagToPost"]] = relationship("TagToPost", back_populates="post", lazy="joined",
                                                            overlaps="tags")

    @validates('tags')
    def validate_tags(self, key, tags):
        if len(tags) > 5:
            raise ValueError("The number of tags cannot be more than 5.")
        return tags


class Tag(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    # posts: Mapped[List["Post"]] = relationship("TagToPost", secondary='tags_to_posts', back_populates='posts')

    tags_to_posts: Mapped[List["TagToPost"]] = relationship("TagToPost", back_populates="tag", lazy="joined",
                                                            overlaps="posts,tags")
    posts: Mapped[List["Post"]] = relationship("Post", secondary="tags_to_posts", back_populates="tags", lazy="joined",
                                               overlaps="tags_to_posts")


class TagToPost(Base):
    __tablename__ = 'tags_to_posts'
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="tags_to_posts", lazy="joined", overlaps="posts,tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="tags_to_posts", lazy="joined", overlaps="posts,tags")


mapper_registry.configure()

# class TagToPost(Base):
#     __tablename__ = 'tags_to_posts'
#     id: Mapped[int] = mapped_column(primary_key=True)
#     post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id'), nullable=False)
#     tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), nullable=False)

