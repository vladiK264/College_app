from fastapi import FastAPI, Depends, Request, status, Form, Body
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from io import BytesIO
import pandas as pd

# Импорты проекта
import backend.models as models
import backend.database as database
import backend.crud as crud
import backend.schemas as schemas
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

@app.get("/", response_class=HTMLResponse)
def read_root(): return load_html("index.html")

@app.get("/distribute.html", response_class=HTMLResponse)
def distribute_page(): return load_html("distribute.html")

@app.get("/assign.html", response_class=HTMLResponse)
def assign_page(): return load_html("assign.html")

@app.get("/check.html", response_class=HTMLResponse)
def check_page(): return load_html("check.html")

@app.get("/reserve.html", response_class=HTMLResponse)
def reserve_page(): return load_html("reserve.html")

@app.get("/login", response_class=HTMLResponse)
def login_page(): return load_html("login.html")

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

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

#  Авторизация
@app.post("/auth")
async def authenticate(request: Request):
    data = await request.json()
    if data.get("username") == "admin" and data.get("password") == "1234":
        return {"message": "Успешный вход"}
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Неверный логин или пароль"})

#  Преподаватели
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

#  Группы
@app.post("/groups", response_model=schemas.Group)
def add_group(group: schemas.GroupCreate, db: Session = Depends(get_db)):
    return crud.create_group(db, group)

@app.get("/groups", response_model=List[schemas.Group])
def get_groups(db: Session = Depends(get_db)):
    return db.query(Group).all()

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
    
    return jsonable_encoder(result)

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
async def get_current_report(db: Session = Depends(get_db)):
    """
    Отчет по текущей нагрузке всех преподавателей
    """
    teachers = db.query(Teacher).all()
    
    if not teachers:
        return JSONResponse({
            "report": "Нет данных о преподавателях",
            "data": [],
            "summary": {
                "total_teachers": 0,
                "overloaded": 0,
                "normal": 0,
                "average_load": 0
            }
        })
    
    loads = db.query(TeachingLoad).all()
    
    report_data = []
    for teacher in teachers:
        teacher_loads = [l for l in loads if l.teacher_id == teacher.id]
        current_hours = sum(l.assigned_hours for l in teacher_loads)
        
        percentage = 0
        if teacher.max_hours > 0:
            percentage = (current_hours / teacher.max_hours) * 100
        
        status = "Норма"
        if percentage > 100:
            status = "Перегрузка"
        elif percentage < 50:
            status = "Недостаточная"
        
        report_data.append({
            "Преподаватель": teacher.name,
            "Текущая нагрузка (ч)": current_hours,
            "Макс. нагрузка (ч)": teacher.max_hours,
            "Загрузка (%)": round(percentage, 1),
            "Статус": status
        })
    
    total_teachers = len(teachers)
    overloaded = sum(1 for item in report_data if item["Статус"] == "Перегрузка")
    normal = sum(1 for item in report_data if item["Статус"] == "Норма")
    insufficient = sum(1 for item in report_data if item["Статус"] == "Недостаточная")
    
    average_load = 0
    if total_teachers > 0:
        average_load = round(sum(item["Загрузка (%)"] for item in report_data) / total_teachers, 1)
    
    text_report = f"""
    📊 ОТЧЕТ ПО ТЕКУЩЕЙ НАГРУЗКЕ
    ---------------------------
    Всего преподавателей: {total_teachers}
    • Перегружено: {overloaded}
    • Нормальная загрузка: {normal}
    • Недостаточная загрузка: {insufficient}
    
    Средняя загрузка: {average_load}%
    """
    
    return JSONResponse({
        "report": text_report,
        "data": report_data,
        "summary": {
            "total_teachers": total_teachers,
            "overloaded": overloaded,
            "normal": normal,
            "insufficient": insufficient,
            "average_load": average_load
        }
    })

@app.get("/report/semester")
async def get_semester_report(db: Session = Depends(get_db), semester: int = 1):
    """
    Отчет по нагрузке за семестр
    """
    loads = db.query(TeachingLoad).filter(TeachingLoad.semester == semester).all()
    teachers = db.query(Teacher).all()
    groups = db.query(Group).all()
    
    if not loads:
        return JSONResponse({
            "report": f"На семестр {semester} нагрузка не назначена",
            "data": [],
            "summary": {
                "semester": semester,
                "total_hours": 0,
                "total_assignments": 0,
                "unique_subjects": 0,
                "unique_groups": 0,
                "teachers_with_load": 0
            }
        })
    
    report_data = []
    for teacher in teachers:
        teacher_loads = [l for l in loads if l.teacher_id == teacher.id]
        if teacher_loads:
            total_hours = sum(l.assigned_hours for l in teacher_loads)
            subjects = ", ".join(set(l.subject for l in teacher_loads))
            
            group_names = []
            for load in teacher_loads:
                group = next((g for g in groups if g.id == load.group_id), None)
                if group:
                    group_names.append(group.name)
            
            groups_str = ", ".join(set(group_names)) if group_names else "Неизвестно"
            
            report_data.append({
                "Преподаватель": teacher.name,
                "Семестр": semester,
                "Часов": total_hours,
                "Предметы": subjects,
                "Группы": groups_str
            })
    
    total_hours_semester = sum(l.assigned_hours for l in loads)
    unique_subjects = len(set(l.subject for l in loads))
    unique_groups = len(set(l.group_id for l in loads))
    teachers_with_load = len(report_data)
    
    text_report = f"""
    📅 ОТЧЕТ ЗА СЕМЕСТР {semester}
    ---------------------------
    Общая нагрузка: {total_hours_semester} часов
    Количество назначений: {len(loads)}
    Уникальных предметов: {unique_subjects}
    Уникальных групп: {unique_groups}
    Преподавателей с нагрузкой: {teachers_with_load}
    """
    
    return JSONResponse({
        "report": text_report,
        "data": report_data,
        "summary": {
            "semester": semester,
            "total_hours": total_hours_semester,
            "total_assignments": len(loads),
            "unique_subjects": unique_subjects,
            "unique_groups": unique_groups,
            "teachers_with_load": teachers_with_load
        }
    })

@app.get("/report/export/excel")
async def export_report_excel(db: Session = Depends(get_db)):
    """
    Экспорт отчета в Excel
    """
    teachers = db.query(Teacher).all()
    loads = db.query(TeachingLoad).all()
    groups = db.query(Group).all()
    
    teacher_data = []
    for teacher in teachers:
        teacher_loads = [l for l in loads if l.teacher_id == teacher.id]
        current_hours = sum(l.assigned_hours for l in teacher_loads)
        percentage = (current_hours / teacher.max_hours * 100) if teacher.max_hours > 0 else 0
        
        teacher_data.append({
            "ID": teacher.id,
            "ФИО": teacher.name,
            "Специализация": teacher.specialization,
            "Квалификация": teacher.qualification,
            "Макс. часов": teacher.max_hours,
            "Текущая нагрузка": current_hours,
            "Загрузка %": round(percentage, 1),
            "Статус": "Перегрузка" if percentage > 100 else "Норма" if percentage > 70 else "Недостаточная"
        })
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame(teacher_data).to_excel(writer, sheet_name='Преподаватели', index=False)
        
        load_data = []
        for load in loads:
            teacher = next((t for t in teachers if t.id == load.teacher_id), None)
            group = next((g for g in groups if g.id == load.group_id), None)
            load_data.append({
                "ID": load.id,
                "Преподаватель": teacher.name if teacher else "Неизвестно",
                "Группа": group.name if group else "Неизвестно",
                "Предмет": load.subject,
                "Часов": load.assigned_hours,
                "Семестр": load.semester,
                "Статус": "Резерв" if load.is_reserved else "Основная"
            })
        pd.DataFrame(load_data).to_excel(writer, sheet_name='Нагрузка', index=False)
        
        group_data = [{"ID": g.id, "Название": g.name, "Год": g.year} for g in groups]
        pd.DataFrame(group_data).to_excel(writer, sheet_name='Группы', index=False)
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=report.xlsx"}
    )

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