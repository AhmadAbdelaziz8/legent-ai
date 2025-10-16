from pydantic import BaseModel
from datetime import datetime


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

