from pydantic import BaseModel
from typing import Any

class MessageData(BaseModel):
    type: int
    data: Any

class DirectMessage(BaseModel):
    type: int = 0
    target: str
    data: MessageData
   
class SubscribeMessage(BaseModel):
    type: int = 1
    data: MessageData
   
class BroadcastMessage(BaseModel):
    type: int = 2
    data: MessageData