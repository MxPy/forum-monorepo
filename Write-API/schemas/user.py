from pydantic import BaseModel
from fastapi import UploadFile

class User(BaseModel):
    userId: str
    nickName: str