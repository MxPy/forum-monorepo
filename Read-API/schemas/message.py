from pydantic import BaseModel


class Message(BaseModel):
    type: int
    destination: str
    body: str