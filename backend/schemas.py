from pydantic import BaseModel

class TeacherCreate(BaseModel):
    name: str
    specialization: str
    qualification: str
    max_hours: int

class Teacher(TeacherCreate):
    id: int

    class Config:
        from_attributes = True  # заменяет orm_mode в Pydantic v2

class Teacher(BaseModel):
    id: int
    name: str
    specialization: str
    qualification: str
    max_hours: int

    class Config:
        orm_mode = True