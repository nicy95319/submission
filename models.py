from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # author 或 editor

class SubmissionModel(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default="編輯中")