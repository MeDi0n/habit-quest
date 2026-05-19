# ============================================================
# services/habit_service.py — Бизнес-логика привычек
# ============================================================
# Этот файл решает ЧТО делать:
# - Проверяет существует ли привычка
# - Вызывает repository для работы с базой
# - Кидает ошибки если что-то не так
#
# Не знает про HTTP (запросы, ответы, статус-коды).
# Не лезет в базу напрямую — только через repository.
# ============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Habit
from app.repositories import habit_repository


def get_all_habits(db: Session, user_id: int) -> list[Habit]:
    """Получить все привычки пользователя."""
    return habit_repository.get_habits_by_user(db, user_id)


def get_habit(db: Session, habit_id: int, user_id: int) -> Habit:
    """Получить привычку. Кинуть ошибку если не найдена."""
    habit = habit_repository.get_habit_by_id(db, habit_id, user_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Привычка не найдена")
    return habit


def create_habit(db: Session, user_id: int, name: str, icon: str, base_xp: int) -> Habit:
    """Создать новую привычку."""
    return habit_repository.create_habit(db, user_id, name, icon, base_xp)


def update_habit(db: Session, habit_id: int, user_id: int, **kwargs) -> Habit:
    """Обновить привычку."""
    habit = get_habit(db, habit_id, user_id)  # проверит что существует
    return habit_repository.update_habit(db, habit, **kwargs)


def delete_habit(db: Session, habit_id: int, user_id: int) -> None:
    """Удалить привычку."""
    habit = get_habit(db, habit_id, user_id)  # проверит что существует
    habit_repository.delete_habit(db, habit)
