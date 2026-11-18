from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String)  # 'author' 或 'editor'

class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String)
    content = Column(String)
    status = Column(String, default="編輯中")  # 編輯中、審查中、已通過
    author_id = Column(Integer, ForeignKey("users.id"))
    
    author = relationship("User")