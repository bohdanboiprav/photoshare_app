# step1 poetry add alembic
# step2 poetry add sqlalchemy
# step3 poetry add psycopg2
#
# step4 створення міграції - alembic init migrations
#
# step5 В migrations/env.py
#       додати    import asyncio
#                 from sqlalchemy.engine import Connection
#                 from sqlalchemy.ext.asyncio import async_engine_from_config
#                 from src.config.config import config as app_config
#                 from src.entity.models import Base
#
#       змінити   target_metadata = Base.metadata
#                 config.set_main_option("sqlalchemy.url", app_config.SQLALCHEMY_DATABASE_URL)
#
#                 def run_migrations(connection: Connection):
#                     context.configure(connection=connection, target_metadata=target_metadata)
#                     with context.begin_transaction():
#                         context.run_migrations()
#                
#                async def run_async_migrations():
#                    connectable = async_engine_from_config(
#                    config.get_section(config.config_ini_section, {}),
#                    prefix="sqlalchemy.",
#                    poolclass=pool.NullPool,
#                     )
#                    async with connectable.connect() as connection:
#                        await connection.run_sync(run_migrations)
#                    await connectable.dispose()
#
#                def run_migrations_online() -> None:
#                    asyncio.run(run_async_migrations())
#
#  step6   Створюємо міграцію -   alembic revision --autogenerate -m 'Init'
#  step7   застосуємо створену міграцію,оновлення таблиць -  alembic upgrade head
#
#  примітка : повинен бути налаштований доступ до бази данних
#
#
#

import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Boolean, func, Table,Enum
from sqlalchemy.orm import relationship ,Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Photo(Base):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(255),nullable=False, unique=True)
    note: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(255))
    qr_url: Mapped[str] = mapped_column(String(255))
    teg_1: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), nullable=False)
    teg_2: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), nullable=False)
    teg_3: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), nullable=False)
    teg_4: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), nullable=False)
    teg_5: Mapped[int] = mapped_column(Integer, ForeignKey('tags.id'), nullable=False)
    create_date = Column('createdat', DateTime, default=func.now())  
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(),
                                             nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", backref="todos", lazy="joined")

class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    nick_name: Mapped[str] = mapped_column(String(50),nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    block: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[str] = mapped_column(String(255))
    create_date = Column('createdat', DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photos.id'), nullable=False)
    block: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)



class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    tag_name: Mapped[str] = mapped_column(String(50),nullable=False, unique=True)


class Rating(Base):
    __tablename__ = "rating"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey('photos.id'), nullable=False)
    rating: Mapped[int] = mapped_column(primary_key=True)
    create_date = Column('createdat', DateTime, default=func.now())