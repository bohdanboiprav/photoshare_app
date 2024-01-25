from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "postgresql+asyncpg://admin:$1234567@$name/$name"
    SECRET_KEY_JWT: str = "secret"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: str = "admin@meta.ua"
    MAIL_PASSWORD: str = "123456789"
    MAIL_FROM: str = "example@meta.ua"
    MAIL_PORT: int = 567234
    MAIL_SERVER: str = "example.meta.ua"
    MAIL_USE_SSL: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 23131
    REDIS_PASSWORD: str | None = None
    CLOUDINARY_NAME: str = "admin"
    CLOUDINARY_API_KEY: str = "a1221d111d1"
    CLOUDINARY_API_SECRET: str = "secret"
    APP_ENV: str = "dev"
    ADMIN_PASSWORD: str = "password"


settings = Settings()
