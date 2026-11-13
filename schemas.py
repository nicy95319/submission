from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class SubmissionCreate(BaseModel):
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

    class Config:
        from_attributes = True