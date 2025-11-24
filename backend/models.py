from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

# 👨‍🏫 Преподаватель
class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    qualification = Column(String, nullable=False)
    max_hours = Column(Integer, nullable=False)

    loads = relationship("TeachingLoad", back_populates="teacher", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Teacher(id={self.id}, name='{self.name}')>"

# 👥 Группа
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    year = Column(Integer, nullable=False)

    loads = relationship("TeachingLoad", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}', year={self.year})>"

# 📚 Нагрузка
class TeachingLoad(Base):
    __tablename__ = "teaching_loads"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    subject = Column(String, nullable=False, index=True)
    assigned_hours = Column(Integer, nullable=False)
    completed_hours = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False, index=True)
    is_reserved = Column(Boolean, default=False)

    teacher = relationship("Teacher", back_populates="loads")
    group = relationship("Group", back_populates="loads")

    def __repr__(self):
        return f"<TeachingLoad(id={self.id}, subject='{self.subject}', semester={self.semester})>"

# 👤 Пользователь
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"