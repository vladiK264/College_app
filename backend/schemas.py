from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import BaseModel



class TeacherCreate(BaseModel):
    name: str
    specialization: str
    qualification: str
    max_hours: int

class Teacher(BaseModel):
    id: int
    name: str
    specialization: str
    qualification: str
    max_hours: int

    class Config:
        from_attributes = True




class GroupCreate(BaseModel):
    name: str
    year: Optional[int] = None

class Group(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True




class TeachingLoadCreate(BaseModel):
    teacher_id: int
    group_id: int
    subject: Optional[str] = "Общее"
    assigned_hours: int
    completed_hours: Optional[int] = 0
    semester: Optional[int] = 1 
    is_reserved: bool = False

class TeachingLoad(BaseModel):
    id: int
    teacher_id: int
    group_id: int
    subject: str
    assigned_hours: int
    completed_hours: int
    semester: int
    is_reserved: bool

    class Config:
        from_attributes = True




class TeachingLoadDetailed(BaseModel):
    id: int
    subject: str
    assigned_hours: int
    completed_hours: int
    semester: int
    is_reserved: bool
    teacher: Teacher
    group: Group

    class Config:
        from_attributes = True




class TeachingLoadReport(BaseModel):
    teacher: str
    group: str
    subject: str
    assigned_hours: int
    completed_hours: int



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

class GroupCreate(BaseModel):
    name: str
    year: int



class TeacherUpdate(BaseModel):
    specialization: str
    qualification: str
    max_hours: int