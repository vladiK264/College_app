from sqlalchemy.orm import Session
import backend.models as models
import backend.schemas as schemas
from backend.models import Teacher, Group, TeachingLoad
from backend.schemas import TeacherUpdate

def get_teachers(db: Session):
    return db.query(models.Teacher).all()

def create_teacher(db: Session, teacher: schemas.TeacherCreate):
    db_teacher = models.Teacher(**teacher.model_dump())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def delete_teacher(db: Session, teacher_id: int):
    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if teacher:
        db.delete(teacher)
        db.commit()
        return True
    return False


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str, token: str):
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        verification_token=token
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def confirm_user_email(db: Session, token: str):
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.commit()
        return True
    return False

def create_group(db: Session, group: schemas.GroupCreate):
    db_group = models.Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def update_teacher(db: Session, teacher_id: int, data: TeacherUpdate):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher:
        teacher.specialization = data.specialization
        teacher.qualification = data.qualification
        teacher.max_hours = data.max_hours
        db.commit()
        db.refresh(teacher)
        return teacher
    return None