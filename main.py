from typing import List

from database import engine, get_db
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
import models
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 自動檢查並在 PostgreSQL 中建立對應的表格
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="投稿審查系統 API")

# 設定 Jinja2 模板資料夾 (對應 templates/index.html)
templates = Jinja2Templates(directory="templates")


# ==========================================
# Pydantic Schemas (資料驗證模型)
# ==========================================
class SubmissionCreate(BaseModel):
    title: str
    category: str
    content: str
    author_id: int = 1


class ReviewRequest(BaseModel):
    status: str  # 通過 或 退回


class SubmissionResponse(BaseModel):
    id: int
    title: str
    category: str
    content: str
    author_id: int
    status: str

    class Config:
        from_attributes = True


# ==========================================
# 前端網頁路由
# ==========================================
@app.get("/")
def read_root(request: Request):
    """回傳前端 HTML 畫面 (templates/index.html)"""
    return templates.TemplateResponse("index.html", {"request": request})


# ==========================================
# 後端 API 路由
# ==========================================

# 1. 新增投稿 (POST)
@app.post("/api/submissions", response_model=SubmissionResponse, status_code=201)
def create_submission(sub: SubmissionCreate, db: Session = Depends(get_db)):
    new_sub = models.Submission(
        title=sub.title,
        category=sub.category,
        content=sub.content,
        author_id=sub.author_id,
        status="審查中"
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub


# 2. 取得所有投稿清單 (GET)
@app.get("/api/author/submissions", response_model=List[SubmissionResponse])
def get_author_submissions(db: Session = Depends(get_db)):
    submissions = db.query(models.Submission).all()
    return submissions


# 3. 編輯/審查投稿狀態 (PATCH)
@app.patch("/api/editor/submissions/{sub_id}/review", response_model=SubmissionResponse)
def review_submission(sub_id: int, review: ReviewRequest, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到該筆投稿")

    if review.status not in ["通過", "退回"]:
        raise HTTPException(status_code=400, detail="審查狀態只能為 '通過' 或 '退回'")

    sub.status = review.status
    db.commit()
    db.refresh(sub)
    return sub