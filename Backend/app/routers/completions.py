# ============================================================
# routers/completions.py — Выполнение привычек
# ============================================================
# Самая интересная часть! Здесь происходит:
#
# 1. Пользователь нажимает ✅ на привычке
# 2. Сервер считает текущий streak (сколько дней подряд)
# 3. Вычисляет множитель и XP
# 4. Сохраняет запись в БД
# 5. Возвращает результат: "+48 XP (×1.6)"
#
# Streak считается так:
# - Смотрим все даты выполнения привычки
# - Идём назад от вчера: если вчера было, позавчера было, и т.д.
# - Как только находим пропуск — streak = количество непрерывных дней + 1
# ============================================================

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Habit, HabitCompletion
from app.schemas import CompletionResponse, HabitWithStats
from app.dependencies import get_current_user
from app.xp_system import calculate_xp, get_streak_multiplier

router = APIRouter(prefix="/completions", tags=["Completions"])


def _calculate_streak(db: Session, habit_id: int, up_to_date: date) -> int:
    """
    Считает текущий streak (серию дней подряд) для привычки.

    Логика:
    1. Берём все даты выполнения, сортируем по убыванию
    2. Проверяем: был ли выполнен вчера? Позавчера? И т.д.
    3. Как только находим пропущенный день — останавливаемся

    Пример:
        Сегодня 22 апреля. Выполнения: 21, 20, 19, 17 апреля.
        Streak = 3 (21, 20, 19 — подряд, 18 пропущен).
        Если сегодня тоже выполнили — streak будет 4.
    """
    # Получаем все даты выполнения (уникальные, по убыванию)
    completion_dates = (
        db.query(HabitCompletion.completed_date)
        .filter(HabitCompletion.habit_id == habit_id)
        .distinct()
        .order_by(HabitCompletion.completed_date.desc())
        .all()
    )

    # Преобразуем в множество дат для быстрого поиска
    # set() — неупорядоченная коллекция, поиск в ней O(1)
    date_set = {row.completed_date for row in completion_dates}

    # Считаем дни подряд, начиная со вчера
    streak = 0
    check_date = up_to_date - timedelta(days=1)

    while check_date in date_set:
        streak += 1
        check_date -= timedelta(days=1)

    # +1 за сегодняшний день (если сегодня выполнено)
    if up_to_date in date_set:
        streak += 1

    return max(streak, 1)  # Минимум 1 (первый день)


@router.post("/{habit_id}", response_model=CompletionResponse)
def complete_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Отметить привычку как выполненную сегодня.

    POST /completions/5

    Если привычка уже выполнена сегодня — вернёт ошибку 400.
    """
    today = date.today()

    # Проверяем что привычка существует и принадлежит пользователю
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=404, detail="Привычка не найдена")

    # Проверяем не выполнена ли уже сегодня
    existing = (
        db.query(HabitCompletion)
        .filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completed_date == today,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Привычка уже выполнена сегодня"
        )

    # Считаем streak (до сегодня + сегодня)
    streak = _calculate_streak(db, habit_id, today)

    # Считаем XP
    earned_xp, multiplier = calculate_xp(habit.base_xp, streak)

    # Сохраняем выполнение
    completion = HabitCompletion(
        habit_id=habit_id,
        completed_date=today,
        xp_earned=earned_xp,
        streak_at_completion=streak,
    )
    db.add(completion)
    db.commit()

    return CompletionResponse(
        habit_id=habit_id,
        completed_date=today,
        xp_earned=earned_xp,
        streak=streak,
        multiplier=multiplier,
        message=f"{habit.icon} {habit.name} выполнено! +{earned_xp} XP (×{multiplier})",
    )


@router.delete("/{habit_id}", status_code=200)
def uncomplete_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Отменить выполнение привычки за сегодня (убрать галочку).

    DELETE /completions/5
    """
    today = date.today()

    # Проверяем что привычка принадлежит пользователю
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == user.id)
        .first()
    )
    if not habit:
        raise HTTPException(status_code=404, detail="Привычка не найдена")

    completion = (
        db.query(HabitCompletion)
        .filter(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completed_date == today,
        )
        .first()
    )
    if not completion:
        raise HTTPException(
            status_code=400, detail="Привычка не была выполнена сегодня"
        )

    db.delete(completion)
    db.commit()

    return {"message": f"Выполнение {habit.name} отменено"}


@router.get("/today", response_model=list[HabitWithStats])
def get_today_habits(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Получить все привычки на сегодня с их статистикой.

    GET /completions/today

    Это главный эндпоинт для страницы "Today" в макете.
    Возвращает каждую привычку + streak, XP, множитель, выполнена ли.
    """
    today = date.today()

    habits = (
        db.query(Habit)
        .filter(Habit.user_id == user.id, Habit.is_active == True)
        .order_by(Habit.created_at)
        .all()
    )

    result = []
    for habit in habits:
        # Проверяем выполнена ли сегодня
        today_completion = (
            db.query(HabitCompletion)
            .filter(
                HabitCompletion.habit_id == habit.id,
                HabitCompletion.completed_date == today,
            )
            .first()
        )

        streak = _calculate_streak(db, habit.id, today)
        multiplier = get_streak_multiplier(streak)

        result.append(
            HabitWithStats(
                id=habit.id,
                name=habit.name,
                icon=habit.icon,
                base_xp=habit.base_xp,
                is_active=habit.is_active,
                created_at=habit.created_at,
                current_streak=streak,
                is_completed_today=today_completion is not None,
                xp_today=today_completion.xp_earned if today_completion else 0,
                multiplier=multiplier,
            )
        )

    return result
