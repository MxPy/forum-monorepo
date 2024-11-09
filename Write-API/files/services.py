from fastapi import UploadFile

from files.client import MinioClient
from files.settings import settings
import logging

logger = logging.getLogger()

async def upload_file(
    user_id: str, bucket_name: str, file: UploadFile
) -> dict | None:
    logger.info("upload file")
    client = MinioClient(
        bucket_name=bucket_name,
    )
    client.upload_file(file=file)
    return {"path":f"http://localhost:9000/{bucket_name}/{file.filename}"}


async def download_file(
    user_id: str, bucket_name: str, file_path: str
) -> str | None:
    client = MinioClient(
        bucket_name=bucket_name,
    )
    destination_folder = f"{settings.TEMP_FOLDER}/{user_id}"
    filename = file_path.split("/")[-1]
    client.download_file(
        source=file_path, destination=f"{destination_folder}/{filename}"
    )
    return f"{destination_folder}/{filename}"