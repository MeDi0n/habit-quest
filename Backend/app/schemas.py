# ============================================================
# schemas.py — Схемы данных (Pydantic)
# ============================================================
# Pydantic — это библиотека для валидации данных.
#
# Зачем нужно: когда пользователь отправляет JSON на сервер,
# нужно проверить что данные корректны. Например:
# - email должен быть правильным email'ом
# - имя привычки не должно быть пустым
# - base_xp должен быть числом > 0
#
# Pydantic делает это автоматически. Если данные невалидны,
# FastAPI сам вернёт ошибку 422 с описанием что не так.
#
# Разница между Models и Schemas:
# - Models (models.py) = структура БАЗЫ ДАННЫХ (таблицы)
# - Schemas (этот файл) = структура JSON ЗАПРОСОВ/ОТВЕТОВ
# ============================================================

from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field


# ─── Авторизация ───

class UserRegister(BaseModel):
    """Что присылает пользователь при регистрации."""
    email: EmailStr                          # Валидация email встроена
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    """Что присылает пользователь при входе."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Что сервер возвращает после логина — JWT токен."""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Публичная информация о пользователе (без пароля!)."""
    id: int
    email: str
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}
    # from_attributes = True позволяет создавать схему из SQLAlchemy-объекта:
    # UserResponse.model_validate(db_user) сконвертирует ORM-объект в JSON


# ─── Привычки ───

class HabitCreate(BaseModel):
    """Данные для создания новой привычки."""
    name: str = Field(min_length=1, max_length=100)
    icon: str = Field(default="⭐", max_length=10)
    base_xp: int = Field(default=20, ge=5, le=100)  # ge = greater or equal


class HabitUpdate(BaseModel):
    """Данные для обновления привычки (все поля опциональны)."""
    name: str | None = Field(default=None, min_length=1, max_length=100)
    icon: str | None = Field(default=None, max_length=10)
    base_xp: int | None = Field(default=None, ge=5, le=100)
    is_active: bool | None = None


class HabitResponse(BaseModel):
    """Привычка как она возвращается клиенту."""
    id: int
    name: str
    icon: str
    base_xp: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class HabitWithStats(HabitResponse):
    """Привычка + её текущая статистика (для страницы Today)."""
    current_streak: int = 0
    is_completed_today: bool = False
    xp_today: int = 0
    multiplier: float = 1.0


# ─── Выполнения ───

class CompletionResponse(BaseModel):
    """Ответ после выполнения привычки."""
    habit_id: int
    completed_date: date
    xp_earned: int
    streak: int
    multiplier: float
    message: str  # "Morning Exercise completed! +48 XP (×1.6)"


# ─── Статистика ───

class StatsResponse(BaseModel):
    """Общая статистика пользователя."""
    completed_today: int
    total_habits: int
    longest_streak: int
    total_xp: int
    total_streak_days: int
    level: int
    level_name: str
    xp_in_current_level: int     # Сколько XP набрано в текущем уровне
    xp_for_next_level: int       # Сколько нужно для следующего уровня
    habit_streaks: list[dict]    # Streak по каждой привычке


# ─── Профиль ───

class ProfileResponse(BaseModel):
    """Данные для страницы профиля."""
    username: str
    email: str
    level: int
    level_name: str
    total_xp: int
    xp_in_current_level: int
    xp_for_next_level: int
    character_stage: int          # Стадия эволюции персонажа (0-8)
    member_since: datetime
