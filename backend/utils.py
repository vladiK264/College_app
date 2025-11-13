from passlib.context import CryptContext
from pydantic import EmailStr
import uuid
import bcrypt

# Настройка bcrypt-хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt принимает максимум 72 байта
    trimmed = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return bcrypt.hashpw(trimmed.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def generate_token() -> str:
    """Генерирует уникальный токен (например, для подтверждения email)."""
    return str(uuid.uuid4())