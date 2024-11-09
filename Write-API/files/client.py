from fastapi import HTTPException, UploadFile, status
from minio import Minio

from files.utils import file_size
from files.settings import settings
import logging

logger = logging.getLogger()


class MinioClient:
    def __init__(
        self, bucket_name: str
    ):
        self.client = Minio(f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.ACCESS_KEY,
            secret_key=settings.SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = bucket_name

    def create_bucket(self):
        logger.info("create bucket")
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_file(self, file: UploadFile):
        logger.info("upload file")
        try:
            #temp
            #self.create_bucket()
            #temp
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=file.filename,
                data=file.file,
                length=file_size(file),
            )
        except Exception as e:
            self._exception(f"Error while trying to upload file. Exception: {e}")

    def download_file(self, source: str, destination: str):
        try:
            self.client.fget_object(self.bucket_name, source, destination)
        except Exception as e:
            self._exception(f"Error while trying to download file. Exception: {e}")

    def _exception(self, detail: str):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )