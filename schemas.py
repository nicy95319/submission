<<<<<<< HEAD
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
=======
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
>>>>>>> be88a119ce8e4ff0c83de91db2331c0359056666
        from_attributes = True