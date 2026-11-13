<<<<<<< HEAD
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
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

# 啟動時自動建立預設作者與編輯帳號
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    # 建立作者
    author = db.query(models.User).filter(models.User.id == 1).first()
    if not author:
        db.add(models.User(id=1, username="作者小澄", password="123", role="author"))
    
    # 建立編輯
    editor = db.query(models.User).filter(models.User.id == 2).first()
    if not editor:
        db.add(models.User(id=2, username="主編森活", password="123", role="editor"))
    
    db.commit()
    db.close()

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

# 登入驗證 API
@app.post("/api/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username, models.User.password == data.password).first()
    if not user:
        raise HTTPException(status_code=400, detail="帳號或密碼錯誤")
    return {"role": user.role, "username": user.username, "user_id": user.id}

# 作者新增投稿
@app.post("/api/submissions", response_model=schemas.SubmissionResponse)
def create_submission(submission: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    db_sub = models.Submission(
        title=submission.title,
        category=submission.category,
        content=submission.content,
        author_id=1,  # 預設由作者送出
        status="編輯中"
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

# 取得所有投稿清單
@app.get("/api/submissions", response_model=list[schemas.SubmissionResponse])
def get_submissions(db: Session = Depends(get_db)):
    return db.query(models.Submission).all()

# 編輯審核：更新狀態 (通過 / 退回)
@app.put("/api/submissions/{sub_id}/status")
def update_status(sub_id: int, status_data: dict, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此投稿")
    sub.status = status_data.get("status")
    db.commit()
=======
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
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

# 啟動時自動建立預設作者與編輯帳號
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    # 建立作者
    author = db.query(models.User).filter(models.User.id == 1).first()
    if not author:
        db.add(models.User(id=1, username="作者小澄", password="123", role="author"))
    
    # 建立編輯
    editor = db.query(models.User).filter(models.User.id == 2).first()
    if not editor:
        db.add(models.User(id=2, username="主編森活", password="123", role="editor"))
    
    db.commit()
    db.close()

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

# 登入驗證 API
@app.post("/api/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username, models.User.password == data.password).first()
    if not user:
        raise HTTPException(status_code=400, detail="帳號或密碼錯誤")
    return {"role": user.role, "username": user.username, "user_id": user.id}

# 作者新增投稿
@app.post("/api/submissions", response_model=schemas.SubmissionResponse)
def create_submission(submission: schemas.SubmissionCreate, db: Session = Depends(get_db)):
    db_sub = models.Submission(
        title=submission.title,
        category=submission.category,
        content=submission.content,
        author_id=1,  # 預設由作者送出
        status="編輯中"
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

# 取得所有投稿清單
@app.get("/api/submissions", response_model=list[schemas.SubmissionResponse])
def get_submissions(db: Session = Depends(get_db)):
    return db.query(models.Submission).all()

# 編輯審核：更新狀態 (通過 / 退回)
@app.put("/api/submissions/{sub_id}/status")
def update_status(sub_id: int, status_data: dict, db: Session = Depends(get_db)):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="找不到此投稿")
    sub.status = status_data.get("status")
    db.commit()
>>>>>>> be88a119ce8e4ff0c83de91db2331c0359056666
    return {"message": "狀態更新成功"}