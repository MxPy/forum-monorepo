from functools import lru_cache


from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MINIO_ROOT_USER: str = "username"
    MINIO_ROOT_PASSWORD: str = "password"
    MINIO_HOST: str = "minio"
    MINIO_PORT: int = 9000
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "minio-bucket"
    ACCESS_KEY: str = "7CKtSumUEu14ERHJc2mb"
    SECRET_KEY: str = "xdijMg7jqa6331TImWuxdA5zLdX55yQ3zrCu7Jh9"




@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()