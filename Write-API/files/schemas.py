
from fastapi import UploadFile
from pydantic import BaseModel

from files.utils import form_body


class FileDownload(BaseModel):
    storage_id: str
    file_path: str


@form_body
class FileUpload(BaseModel):
    file: UploadFile
    user_id: str
    bucket_name: str


