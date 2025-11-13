from fastapi import FastAPI, Depends, Request, status, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import backend.models as models
import backend.database as database
import backend.crud as crud
import backend.schemas as schemas
from backend.utils import hash_password, generate_token
from backend.email_utils import send_email

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Главная страница ----------
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("frontend/index.html", encoding="utf-8") as f:
        return f.read()

# ---------- Страница входа ----------
@app.get("/login", response_class=HTMLResponse)
def login_page():
    with open("frontend/login.html", encoding="utf-8") as f:
        return f.read()

# ---------- Страница регистрации ----------
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ---------- Обработка регистрации ----------
@app.post("/register_form")
def register_user(
    email: str = Form(...),
    password: str = Form(...),
    smtp_email: str = Form(...),
    smtp_password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = crud.get_user_by_email(db, email)
    if existing_user:
        return RedirectResponse("/register?error=exists", status_code=303)

    token = generate_token()
    user_create = schemas.UserCreate(email=email, password=password)
    crud.create_user(db, user_create, hash_password(password), token)

    try:
        send_email(
            from_email=smtp_email,
            app_password=smtp_password,
            to_email=email,
            subject="Добро пожаловать!",
            body=f"Вы успешно зарегистрированы. Ваш токен: {token}"
        )
        print("✅ Письмо отправлено успешно.")
    except Exception as e:
        print("❌ Ошибка при отправке письма:", e)

    return RedirectResponse("/register?success=true", status_code=303)

# ---------- Обработка авторизации (заглушка) ----------
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

# ---------- Получение списка преподавателей ----------
@app.get("/teachers", response_model=list[schemas.Teacher])
def list_teachers(db: Session = Depends(get_db)):
    return crud.get_teachers(db)

# ---------- Добавление преподавателя ----------
@app.post("/teachers", response_model=schemas.Teacher)
def add_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    return crud.create_teacher(db, teacher)

# ---------- Удаление преподавателя ----------
@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    if crud.delete_teacher(db, teacher_id):
        return {"message": "Удалено"}
    return {"error": "Не найдено"}

@app.post("/distribute")
def distribute_load():
    # Здесь будет логика распределения
    print("📊 Распределение нагрузки выполнено.")
    return {"message": "Распределение завершено"}