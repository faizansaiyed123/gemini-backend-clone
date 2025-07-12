from pydantic import BaseModel, Field
from typing import Optional

class ChatroomCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
