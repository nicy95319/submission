from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

# 引入你寫好的資料庫連線與模型
from database import get_db
import models

app = FastAPI(title="投稿審查系統 API")

# ==================== 1. 列舉型態定義 (Enum) ====================
class UserRole(str, Enum):
    AUTHOR = "author"
    EDITOR = "editor"

class SubmissionStatus(str, Enum):
    DRAFT = "編輯中"
    REVIEWING = "審查中"
    APPROVED = "已通過"

class ReviewAction(str, Enum):
    APPROVE = "approve"  # 通過
    REJECT = "reject"    # 退回修改


# ==================== 2. Pydantic 請求/回應資料驗證模型 ====================
class SubmissionCreate(BaseModel):
    category: str
    title: str
    content: str
    author_id: int

class SubmissionUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None


# ==================== 3. 作者端 API ====================

@app.get("/api/author/submissions", summary="查看投稿稿件清單")
def get_author_submissions(author_id: int, db: Session = Depends(get_db)):
    """
    回傳該作者的所有稿件清單 (類別、標題、審查狀態)
    """
    submissions = db.query(models.SubmissionModel).filter(models.SubmissionModel.author_id == author_id).all()
    return submissions

@app.post("/api/submissions", status_code=201, summary="新增投稿")
def create_submission(data: SubmissionCreate, db: Session = Depends(get_db)):
    """
    建立新稿件，狀態預設為「編輯中」
    """
    new_sub = models.SubmissionModel(
        author_id=data.author_id,
        category=data.category,
        title=data.title,
        content=data.content,
        status=SubmissionStatus.DRAFT  # 預設為編輯中
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return {"message": "新增投稿成功", "submission": new_sub}

@app.put("/api/submissions/{sub_id}", summary="編輯投稿")
def update_submission(sub_id: int, data: SubmissionUpdate, author_id: int, db: Session = Depends(get_db)):
    """
    編輯投稿：僅限狀態為「編輯中」的稿件才能修改
    """
    sub = db.query(models.SubmissionModel).filter(models.SubmissionModel.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此稿件")
    
    if sub.author_id != author_id:
        raise HTTPException(status_code=403, detail="您沒有權限修改此稿件")
    
    # 檢查狀態是否為「編輯中」
    if sub.status != SubmissionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能修改狀態為「編輯中」的稿件")
    
    if data.category is not None:
        sub.category = data.category
    if data.title is not None:
        sub.title = data.title
    if data.content is not None:
        sub.content = data.content
        
    db.commit()
    db.refresh(sub)
    return {"message": "更新成功", "submission": sub}

@app.delete("/api/submissions/{sub_id}", summary="刪除稿件")
def delete_submission(sub_id: int, author_id: int, db: Session = Depends(get_db)):
    """
    刪除稿件：僅限狀態為「編輯中」才能刪除
    """
    sub = db.query(models.SubmissionModel).filter(models.SubmissionModel.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此稿件")
        
    if sub.author_id != author_id:
        raise HTTPException(status_code=403, detail="您沒有權限刪除此稿件")
        
    if sub.status != SubmissionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只能刪除狀態為「編輯中」的稿件")
        
    db.delete(sub)
    db.commit()
    return {"message": "刪除成功"}

@app.patch("/api/submissions/{sub_id}/submit", summary="送出投稿")
def submit_for_review(sub_id: int, author_id: int, db: Session = Depends(get_db)):
    """
    送出投稿：將狀態從「編輯中」改為「審查中」
    """
    sub = db.query(models.SubmissionModel).filter(models.SubmissionModel.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此稿件")
        
    if sub.author_id != author_id:
        raise HTTPException(status_code=403, detail="您沒有權限送出此稿件")
        
    if sub.status != SubmissionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="只有「編輯中」的稿件才能送出審查")
        
    sub.status = SubmissionStatus.REVIEWING
    db.commit()
    db.refresh(sub)
    return {"message": "已成功送出審查", "submission": sub}


# ==================== 4. 編輯端 API ====================

@app.get("/api/editor/pending", summary="查看待審查清單")
def get_pending_submissions(db: Session = Depends(get_db)):
    """
    回傳所有狀態為「審查中」的清單 (顯示作者、類別、標題)
    """
    pending_subs = db.query(models.SubmissionModel).filter(models.SubmissionModel.status == SubmissionStatus.REVIEWING).all()
    return pending_subs

@app.get("/api/editor/submissions/{sub_id}", summary="查看稿件詳細內容")
def get_submission_detail(sub_id: int, db: Session = Depends(get_db)):
    """
    回傳特定稿件的詳細內容供編輯閱讀
    """
    sub = db.query(models.SubmissionModel).filter(models.SubmissionModel.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此稿件")
    return sub

@app.patch("/api/editor/submissions/{sub_id}/review", summary="審查操作(通過或退回)")
def review_submission(sub_id: int, action: ReviewAction, db: Session = Depends(get_db)):
    """
    審查操作：
    - approve -> 狀態改為「已通過」 (審查中 => 已通過)
    - reject -> 狀態改為「編輯中」 (審查中 => 編輯中，讓作者修改)
    """
    sub = db.query(models.SubmissionModel).filter(models.SubmissionModel.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此稿件")
        
    if sub.status != SubmissionStatus.REVIEWING:
        raise HTTPException(status_code=400, detail="此稿件目前不在審查中狀態")
        
    if action == ReviewAction.APPROVE:
        sub.status = SubmissionStatus.APPROVED
        message = "審查通過"
    elif action == ReviewAction.REJECT:
        sub.status = SubmissionStatus.DRAFT
        message = "已退回給作者修改"
    else:
        raise HTTPException(status_code=400, detail="無效的操作指令")
        
    db.commit()
    db.refresh(sub)
    return {"message": message, "submission": sub}