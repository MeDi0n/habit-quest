# ============================================================
# routers/stats.py — Статистика и профиль
# ============================================================
# Эндпоинты для страниц Statistics и Profile из макета.
#
# Агрегатные функции SQL:
# - func.sum()   — сумма (сколько всего XP)
# - func.count() — количество (сколько выполнений сегодня)
# - func.max()   — максимум (самый длинный streak)
# ============================================================

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Habit, HabitCompletion
from app.schemas import StatsResponse, ProfileResponse
from app.dependencies import get_current_user
from app.xp_system import get_level_progress
from app.routers.completions import _calculate_streak

router = APIRouter(tags=["Stats"])


def _get_total_xp(db: Session, user_id: int) -> int:
    """Считает общий XP пользователя из всех выполнений."""
    # JOIN — объединяет таблицы. Здесь мы соединяем HabitCompletion с Habit,
    # чтобы отфильтровать только привычки текущего пользователя.
    result = (
        db.query(func.sum(HabitCompletion.xp_earned))
        .join(Habit, HabitCompletion.habit_id == Habit.id)
        .filter(Habit.user_id == user_id)
        .scalar()  # scalar() — вернёт одно значение (не строку)
    )
    return result or 0  # Если None (нет данных) → 0


def _get_longest_streak(db: Session, user_id: int) -> int:
    """Находит самый длинный streak среди всех привычек пользователя."""
    habits = db.query(Habit).filter(Habit.user_id == user_id).all()
    if not habits:
        return 0

    # Берём максимальный streak_at_completion из всех записей
    result = (
        db.query(func.max(HabitCompletion.streak_at_completion))
        .join(Habit, HabitCompletion.habit_id == Habit.id)
        .filter(Habit.user_id == user_id)
        .scalar()
    )
    return result or 0


def _get_total_streak_days(db: Session, user_id: int) -> int:
    """Считает сумму текущих стриков по всем привычкам."""
    habits = (
        db.query(Habit)
        .filter(Habit.user_id == user_id, Habit.is_active == True)
        .all()
    )
    today = date.today()
    return sum(_calculate_streak(db, h.id, today) for h in habits)


@router.get("/stats", response_model=StatsResponse)
def get_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Общая статистика пользователя.

    GET /stats

    Для страницы Statistics из макета:
    - Completed Today: 5
    - Longest Streak: 8d
    - Total XP: 236
    - Total Streaks: 22d
    - Habit Streaks: прогресс-бары по каждой привычке
    """
    today = date.today()

    # Сколько привычек выполнено сегодня
    completed_today = (
        db.query(func.count(HabitCompletion.id))
        .join(Habit, HabitCompletion.habit_id == Habit.id)
        .filter(
            Habit.user_id == user.id,
            HabitCompletion.completed_date == today,
        )
        .scalar()
    ) or 0

    # Общее количество активных привычек
    total_habits = (
        db.query(func.count(Habit.id))
        .filter(Habit.user_id == user.id, Habit.is_active == True)
        .scalar()
    ) or 0

    total_xp = _get_total_xp(db, user.id)
    longest_streak = _get_longest_streak(db, user.id)
    total_streak_days = _get_total_streak_days(db, user.id)
    level_info = get_level_progress(total_xp)

    # Streak по каждой привычке (для прогресс-баров)
    habits = (
        db.query(Habit)
        .filter(Habit.user_id == user.id, Habit.is_active == True)
        .all()
    )
    habit_streaks = []
    for habit in habits:
        streak = _calculate_streak(db, habit.id, today)
        habit_streaks.append({
            "id": habit.id,
            "name": habit.name,
            "icon": habit.icon,
            "streak": streak,
        })

    return StatsResponse(
        completed_today=completed_today,
        total_habits=total_habits,
        longest_streak=longest_streak,
        total_xp=total_xp,
        total_streak_days=total_streak_days,
        level=level_info["level"],
        level_name=level_info["level_name"],
        xp_in_current_level=level_info["xp_in_current_level"],
        xp_for_next_level=level_info["xp_for_next_level"],
        habit_streaks=habit_streaks,
    )


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Профиль пользователя.

    GET /profile

    Для страницы Profile из макета:
    - Персонаж с уровнем
    - XP прогресс
    - Стадия эволюции
    """
    total_xp = _get_total_xp(db, user.id)
    level_info = get_level_progress(total_xp)

    return ProfileResponse(
        username=user.username,
        email=user.email,
        level=level_info["level"],
        level_name=level_info["level_name"],
        total_xp=total_xp,
        xp_in_current_level=level_info["xp_in_current_level"],
        xp_for_next_level=level_info["xp_for_next_level"],
        character_stage=level_info["character_stage"],
        member_since=user.created_at,
    )
