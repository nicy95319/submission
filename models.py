from database import Base
from sqlalchemy import Column, Integer, String, Text


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False, default=1)
    status = Column(String(50), default="審查中")  # 狀態可為：審查中、通過、退回