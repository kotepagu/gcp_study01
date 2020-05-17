from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, sessionmaker
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import Todo, engine

# DB接続用のセッションクラス インスタンスが作成されると接続する
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydanticを用いたAPIに渡されるデータの定義 ValidationやDocumentationの機能が追加される
class TodoIn(BaseModel):
    title: str
    done: bool

# 単一のTodoを取得するためのユーティリティ
def get_todo(db_session: Session, todo_id: int):
    return db_session.query(Todo).filter(Todo.id == todo_id).first()

# DB接続のセッションを各エンドポイントの関数に渡す
def get_db(request: Request):
    return request.state.db

# このインスタンスをアノテーションに利用することでエンドポイントを定義できる
app = FastAPI()

# CORS回避
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Todoの全取得
@app.get("/todos/")
def read_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos

# 単一のTodoを取得
@app.get("/todos/{todo_id}")
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)
    return todo

# Todoを登録
@app.post("/todos/")
async def create_todo(todo_in: TodoIn,  db: Session = Depends(get_db)):
    todo = Todo(title=todo_in.title, done=False)
    db.add(todo)
    db.commit()
    todo = get_todo(db, todo.id)
    return todo

# Todoを更新
@app.put("/todos/{todo_id}")
async def update_todo(todo_id: int, todo_in: TodoIn, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)
    todo.title = todo_in.title
    todo.done = todo_in.done
    db.commit()
    todo = get_todo(db, todo_id)
    return todo

# Todoを削除
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = get_todo(db, todo_id)
    db.delete(todo)
    db.commit()

# リクエストの度に呼ばれるミドルウェア DB接続用のセッションインスタンスを作成
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    response = await call_next(request)
    request.state.db.close()
    return response

