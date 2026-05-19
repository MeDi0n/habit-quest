# ============================================================
# repositories/habit_repository.py — Работа с базой данных
# ============================================================
# Этот файл ТОЛЬКО достаёт и сохраняет данные.
# Никакой логики. Не знает про XP, стрики, уровни.
# Просто: дай, сохрани, обнови, удали.
# ============================================================

from sqlalchemy.orm import Session
from app.models import Habit


def get_habits_by_user(db: Session, user_id: int) -> list[Habit]:
    """Получить все активные привычки пользователя."""
    return (
        db.query(Habit)
        .filter(Habit.user_id == user_id, Habit.is_active == True)
        .order_by(Habit.created_at)
        .all()
    )


def get_habit_by_id(db: Session, habit_id: int, user_id: int) -> Habit | None:
    """Получить одну привычку (проверяя что она принадлежит пользователю)."""
    return (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == user_id)
        .first()
    )


def create_habit(db: Session, user_id: int, name: str, icon: str, base_xp: int) -> Habit:
    """Создать новую привычку."""
    habit = Habit(
        user_id=user_id,
        name=name,
        icon=icon,
        base_xp=base_xp,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def update_habit(db: Session, habit: Habit, **kwargs) -> Habit:
    """Обновить поля привычки."""
    for key, value in kwargs.items():
        setattr(habit, key, value)
    db.commit()
    db.refresh(habit)
    return habit


def delete_habit(db: Session, habit: Habit) -> None:
    """Удалить привычку."""
    db.delete(habit)
    db.commit()
