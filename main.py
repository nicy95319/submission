from fastapi import FastAPI, Depends, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import models, schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if not db.query(models.User).filter(models.User.id == 1).first():
        db.add(models.User(id=1, username="作者小澄", password="123", role="author"))
    if not db.query(models.User).filter(models.User.id == 2).first():
        db.add(models.User(id=2, username="主編森活", password="123", role="editor"))
    db.commit()
    db.close()

def serialize_sub(sub):
    return {
        "id": sub.id,
        "title": sub.title,
        "category": sub.category,
        "content": sub.content,
        "status": sub.status,
        "author_id": sub.author_id,
        "author_username": sub.author.username if sub.author else "未知作者"
    }

# 頁面路由
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/author", response_class=HTMLResponse)
def author_page(request: Request):
    return templates.TemplateResponse("author.html", {"request": request})

@app.get("/editor", response_class=HTMLResponse)
def editor_page(request: Request):
    return templates.TemplateResponse("editor.html", {"request": request})

# 登入 API
@app.post("/api/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username, models.User.password == data.password).first()
    if not user:
        raise HTTPException(status_code=400, detail="帳號或密碼錯誤")
    return {"role": user.role, "username": user.username, "user_id": user.id}

# 取得投稿列表（可依 author_id 或 status 篩選）
@app.get("/api/submissions")
def get_submissions(author_id: Optional[int] = Query(None), status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(models.Submission)
    if author_id is not None:
        query = query.filter(models.Submission.author_id == author_id)
    if status is not None:
        query = query.filter(models.Submission.status == status)
    subs = query.all()
    return [serialize_sub(sub) for sub in subs]

# 作者新增投稿
@app.post("/api/submissions")
def create_submission(submission: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    db_sub = models.Submission(
        title=submission.title,
        category=submission.category,
        content=submission.content,
        author_id=submission.author_id,
        status="編輯中"
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return serialize_sub(db_sub)

# 作者修改稿件（限編輯中）
@app.put("/api/submissions/{sub_id}")
def update_submission(sub_id: int, data: schemas.SubmissionUpdate, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此投稿")
    if sub.status != "編輯中":
        raise HTTPException(status_code=400, detail="只有編輯中的稿件才能修改")
    
    sub.title = data.title
    sub.category = data.category
    sub.content = data.content
    db.commit()
    return {"message": "修改成功"}

# 作者刪除稿件（限編輯中）
@app.delete("/api/submissions/{sub_id}")
def delete_submission(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此投稿")
    if sub.status != "編輯中":
        raise HTTPException(status_code=400, detail="只有編輯中的稿件才能刪除")
    
    db.delete(sub)
    db.commit()
    return {"message": "刪除成功"}

# 作者送出審查（編輯中 -> 審查中）
@app.put("/api/submissions/{sub_id}/submit")
def submit_for_review(sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此投稿")
    if sub.status != "編輯中":
        raise HTTPException(status_code=400, detail="只有編輯中的稿件才能送出審查")
    
    sub.status = "審查中"
    db.commit()
    return {"message": "已成功送出審查"}

# 編輯審核：更新狀態（審查中 -> 已通過 或 編輯中[被退回]）
@app.put("/api/submissions/{sub_id}/status")
def update_status(sub_id: int, status_data: dict, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此投稿")
    
    new_status = status_data.get("status")
    if new_status not in ["已通過", "編輯中"]:
        raise HTTPException(status_code=400, detail="不合法的狀態")
        
    sub.status = new_status
    db.commit()
    return {"message": "狀態更新成功"}