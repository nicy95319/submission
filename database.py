from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 請替換成你的 PostgreSQL 連線字串 (格式: postgresql://使用者名稱:密碼@localhost:5432/資料庫名稱)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:03250801@localhost:5432/submission"

# 2. 建立資料庫引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. 建立 SessionLocal 類別供後續 API 操作資料庫使用
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 宣告 ORM 模型基底類別
Base = declarative_base()


# 取得資料庫 Session 的 Dependency 函式
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()