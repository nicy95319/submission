from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 請將下面的連線資訊替換成你自己的 PostgreSQL 設定
# 格式：postgresql://帳號:密碼@主機位置:連接埠/資料庫名稱
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:03250801@localhost:5432/submission"

# 建立 SQLAlchemy 引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 建立 SessionLocal 類別（用來與資料庫進行互動的會話）
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 宣告對應資料庫模型的基礎類別
Base = declarative_base()

# 提供給 FastAPI 依賴注入用的函式（每次請求結束後自動關閉資料庫連線）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()