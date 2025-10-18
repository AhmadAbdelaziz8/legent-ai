from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SessionCreate(BaseModel):
    initial_prompt: str
    status: str = "queued"
    provider: str


class Session(BaseModel):
    id: int
    initial_prompt: str
    status: str
    provider: str
    created_at: datetime


class MessageCreate(BaseModel):
    session_id: int
    role: str = Field(...,
                      description="Message's sender role (user, assistant, tool)")
    content: dict = Field(..., description="Message's content as JSON")
    base64_image: Optional[str] = Field(
        None, description="Base64 encoded screenshot image")


class Message(BaseModel):
    id: int
    session_id: int
    role: str
    content: dict
    base64_image: Optional[str] = None
    created_at: datetime
