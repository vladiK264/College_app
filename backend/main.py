from fastapi import FastAPI, Depends, Request, status, Form, Body
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

# Импорты проекта
import backend.models as models
import backend.database as database
import backend.crud as crud
import backend.schemas as schemas
import json
from backend.utils import hash_password, generate_token
from backend.email_utils import send_email
from backend.models import Teacher, Group, TeachingLoad
from backend.schemas import TeachingLoadReport

from fastapi.encoders import jsonable_encoder
# Инициализация FastAPI
app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")
models.Base.metadata.create_all(bind=database.engine)

# Зависимость для подключения к БД



def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Загрузка HTML-файлов
def load_html(filename: str) -> str:
    with open(f"frontend/{filename}", encoding="utf-8") as f:
        return f.read()

# 📄 Страницы

@app.get("/teaching_loads")
def get_teaching_loads(db: Session = Depends(get_db)):
    loads = db.query(TeachingLoad).all()
    result = []
    for load in loads:
        result.append({
            'id': load.id,
            'teacher_id': load.teacher_id,
            'group_id': load.group_id,
            'assigned_hours': load.assigned_hours,
            'completed_hours': load.completed_hours,
            'subject': 'Общее' if load.subject == 'РћР±С‰РµРµ' else load.subject,
            'semester': load.semester,
            'is_reserved': load.is_reserved
        })
    
    return jsonable_encoder(result)  # Используй jsonable_encoder

@app.get("/", response_class=HTMLResponse)
def read_root(): return load_html("index.html")

@app.get("/distribute.html", response_class=HTMLResponse)
def distribute_page(): return load_html("distribute.html")

@app.get("/assign.html", response_class=HTMLResponse)
def assign_page(): return load_html("assign.html")

@app.get("/remove.html", response_class=HTMLResponse)
def remove_page(): return load_html("remove.html")

@app.get("/check.html", response_class=HTMLResponse)
def check_page(): return load_html("check.html")

@app.get("/reserve.html", response_class=HTMLResponse)
def reserve_page(): return load_html("reserve.html")

@app.get("/report_current.html", response_class=HTMLResponse)
def report_current_page(): return load_html("report_current.html")

@app.get("/report_semester.html", response_class=HTMLResponse)
def report_semester_page(): return load_html("report_semester.html")

@app.get("/login", response_class=HTMLResponse)
def login_page(): return load_html("login.html")

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/group_form.html", response_class=HTMLResponse)
def group_form_page(): return load_html("group_form.html")

# 👤 Регистрация
@app.post("/register_form")
def register_user(
    email: str = Form(...),
    password: str = Form(...),
    smtp_email: str = Form(...),
    smtp_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if crud.get_user_by_email(db, email):
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

# 🔐 Авторизация
@app.post("/auth")
async def authenticate(request: Request):
    data = await request.json()
    if data.get("username") == "admin" and data.get("password") == "1234":
        return {"message": "Успешный вход"}
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Неверный логин или пароль"})

# 👨‍🏫 Преподаватели
@app.get("/teachers", response_model=List[schemas.Teacher])
def list_teachers(db: Session = Depends(get_db)):
    return crud.get_teachers(db)

@app.post("/teachers", response_model=schemas.Teacher)
def add_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    return crud.create_teacher(db, teacher)

@app.put("/teachers/{teacher_id}", response_model=schemas.Teacher)
def update_teacher(teacher_id: int, data: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    return crud.update_teacher(db, teacher_id, data)

@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    if crud.delete_teacher(db, teacher_id):
        return {"message": "Удалено"}
    return {"error": "Не найдено"}

# 👥 Группы
@app.post("/groups", response_model=schemas.Group)
def add_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    return crud.create_group(db, group)

@app.get("/groups", response_model=List[schemas.Group])
def get_groups(db: Session = Depends(get_db)):
    return db.query(Group).all()

# 📊 Отчёты
@app.get("/api/report_semestr", response_model=List[TeachingLoadReport])
def report_semestr(semester: int, db: Session = Depends(get_db)):
    query = (
        db.query(
            Teacher.name.label("teacher"),
            Group.name.label("group"),
            TeachingLoad.subject,
            TeachingLoad.assigned_hours,
            TeachingLoad.completed_hours
        )
        .join(TeachingLoad, TeachingLoad.teacher_id == Teacher.id)
        .join(Group, TeachingLoad.group_id == Group.id)
        .filter(TeachingLoad.semester == semester)
        .all()
    )
    return [
        TeachingLoadReport(
            teacher=row.teacher,
            group=row.group,
            subject=row.subject,
            assigned_hours=row.assigned_hours,
            completed_hours=row.completed_hours
        )
        for row in query
    ]

@app.get("/report/current")
def current_report():
    return {"report": "Текущая нагрузка: ..."}

@app.get("/report/semester")
def semester_report():
    return {"report": "Нагрузка за семестр: ..."}

# 📦 Действия с нагрузкой
@app.post("/distribute")
def distribute_load():
    print("📊 Распределение нагрузки выполнено.")
    return {"message": "Распределение завершено"}

@app.post("/assign_load")
def assign_load(data: dict = Body(...), db: Session = Depends(get_db)):
    teacher_id = data.get("teacher_id")
    group_id = data.get("group_id")
    hours = data.get('hours') 
    if not teacher_id or not group_id:
        return JSONResponse(status_code=400, content={"message": "Нужно указать teacher_id и group_id"})

    existing = db.query(TeachingLoad).filter_by(
        teacher_id=teacher_id,
        group_id=group_id,
        subject="Общее",
        semester=1
    ).first()

    if existing:
        return {"message": "Нагрузка уже назначена"}

    load = TeachingLoad(
        teacher_id=teacher_id,
        group_id=group_id,
        subject="Общее",
        assigned_hours=hours,
        completed_hours=0,
        semester=1,
        is_reserved=False
    )
    db.add(load)
    db.commit()
    return {"message": "Нагрузка назначена"}

@app.post("/remove_load")
def remove_load(data: dict = Body(...), db: Session = Depends(get_db)):
    teacher_id = data.get("teacher_id")
    group_id = data.get("group_id")

    if not teacher_id or not group_id:
        return JSONResponse(status_code=400, content={"message": "Нужно указать teacher_id и group_id"})

    deleted = db.query(TeachingLoad).filter_by(
        teacher_id=teacher_id,
        group_id=group_id,
        subject="Общее",
        semester=1
    ).delete()

    db.commit()
    return {"message": "Нагрузка снята" if deleted else "Нагрузка не найдена"}

@app.post("/assign_from_reserve")
def assign_from_reserve():
    return {"message": "Назначено из резерва"}

@app.get("/check_overload")
def check_overload():
    return {"message": "Проверка перегрузки завершена"}

    
@app.get("/teaching_loads", response_model=List[schemas.TeachingLoad])
def get_teaching_loads(db: Session = Depends(get_db)):
    return db.query(TeachingLoad).all()

@app.post("/teaching_loads", response_model=schemas.TeachingLoad)
def create_teaching_load(load: schemas.TeachingLoadCreate, db: Session = Depends(get_db)):
    db_load = TeachingLoad(**load.dict())
    db.add(db_load)
    db.commit()
    db.refresh(db_load)
    return db_load

@app.put("/teaching_loads/{load_id}", response_model=schemas.TeachingLoad)
def update_teaching_load(load_id: int, data: dict, db: Session = Depends(get_db)):
    load = db.query(TeachingLoad).filter(TeachingLoad.id == load_id).first()
    if load:
        for key, value in data.items():
            setattr(load, key, value)
        db.commit()
        db.refresh(load)
        return load
    return None

@app.delete("/teaching_loads/{load_id}")
def delete_teaching_load(load_id: int, db: Session = Depends(get_db)):
    load = db.query(TeachingLoad).filter(TeachingLoad.id == load_id).first()
    if load:
        db.delete(load)
        db.commit()
        return {"message": "Назначение удалено"}
    return {"error": "Назначение не найдено"}

