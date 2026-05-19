# ============================================================
# routers/habits.py — HTTP-эндпоинты привычек
# ============================================================
# Роутер теперь ТОЛЬКО:
# - Принимает запрос
# - Вызывает service
# - Возвращает ответ
#
# Никакой логики. Никакой работы с базой напрямую.
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import HabitCreate, HabitUpdate, HabitResponse
from app.dependencies import get_current_user
from app.services import habit_service

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.post("/", response_model=HabitResponse, status_code=201)
def create_habit(
    data: HabitCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return habit_service.create_habit(db, user.id, data.name, data.icon, data.base_xp)


@router.get("/", response_model=list[HabitResponse])
def get_habits(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return habit_service.get_all_habits(db, user.id)


@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return habit_service.get_habit(db, habit_id, user.id)


@router.patch("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: int,
    data: HabitUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)
    return habit_service.update_habit(db, habit_id, user.id, **update_data)


@router.delete("/{habit_id}", status_code=204)
def delete_habit(
    habit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    habit_service.delete_habit(db, habit_id, user.id)
