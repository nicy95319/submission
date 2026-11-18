from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class SubmissionCreate(BaseModel):
    title: str
    category: str
    content: str
    author_id: int

class SubmissionUpdate(BaseModel):
    title: str
    category: str
    content: str

class SubmissionResponse(BaseModel):
    id: int
    title: str
    category: str
    content: str
    status: str
    author_id: int
    author_username: Optional[str] = None

    class Config:
        from_attributes = True