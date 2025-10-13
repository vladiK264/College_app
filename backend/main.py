from fastapi import FastAPI, Depends, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
import backend.models as models
import backend.database as database
import backend.crud as crud
import backend.schemas as schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Главная страница
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("frontend/index.html", encoding="utf-8") as f:
        return f.read()

# Страница входа
@app.get("/login", response_class=HTMLResponse)
def login_page():
    with open("frontend/login.html", encoding="utf-8") as f:
        return f.read()

# Обработка авторизации
@app.post("/auth")
async def authenticate(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")
    if username == "admin" and password == "1234":
        return {"message": "Успешный вход"}
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Неверный логин или пароль"}
    )

# Получение списка преподавателей
@app.get("/teachers", response_model=list[schemas.Teacher])
def list_teachers(db: Session = Depends(get_db)):
    return crud.get_teachers(db)

# Добавление преподавателя
@app.post("/teachers", response_model=schemas.Teacher)
def add_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    return crud.create_teacher(db, teacher)

@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if teacher:
        db.delete(teacher)
        db.commit()
        return {"message": "Удалено"}
    return {"error": "Не найдено"}