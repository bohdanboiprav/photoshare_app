from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: str
    DATABASE_NAME: str
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_USE_SSL: bool
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str | None = None
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    APP_ENV: str

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8") # noqa


settings = Settings()
