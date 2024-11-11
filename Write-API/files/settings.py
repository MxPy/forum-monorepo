from functools import lru_cache


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MINIO_ROOT_USER: str = "username"
    MINIO_ROOT_PASSWORD: str = "password"
    MINIO_HOST: str = "minio"
    MINIO_PORT: int = 9000
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "minio-bucket"
    ACCESS_KEY: str = "kzv9yenjgAYp9jSXC8kn"
    SECRET_KEY: str = "v0XmQylc895KIvDuO9yK6PMUoPhBL8w6k9fWNZ5y"




@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()