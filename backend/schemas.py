from pydantic import BaseModel, EmailStr

# ---------- Преподаватели ----------

class TeacherCreate(BaseModel):
    name: str
    specialization: str
    qualification: str
    max_hours: int

class Teacher(TeacherCreate):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2: заменяет orm_mode

# ---------- Пользователи ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True