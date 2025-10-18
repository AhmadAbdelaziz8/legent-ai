from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SessionCreate(BaseModel):
    initial_prompt: str
    status: str = "queued"
    provider: str
    model: Optional[str] = None
    system_prompt_suffix: Optional[str] = None
    max_tokens: Optional[int] = None
    thinking_budget: Optional[int] = None
    only_n_most_recent_images: Optional[int] = None
    tool_version: Optional[str] = None


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
