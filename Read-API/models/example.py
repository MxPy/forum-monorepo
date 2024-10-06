from pydantic import (
    BaseModel
)

class Example(BaseModel):
    device_id: str
    client_id: str