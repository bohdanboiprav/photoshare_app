from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "postgresql+asyncpg://postgres:123456@localhost:5432/base"
    SECRET_KEY_JWT: str = "aego6U6wk"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: str = "admin@example.com"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: str = "admin@example.com"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.example.com"
    MAIL_USE_SSL: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLOUDINARY_NAME: str = "cloud_name"
    CLOUDINARY_API_KEY: int = 123456789
    CLOUDINARY_API_SECRET: str = "secret"
    APP_ENV: str = "str"
    ADMIN_PASSWORD: str = "str"

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


settings = Settings()
