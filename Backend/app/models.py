# ============================================================
# models.py — Модели базы данных (таблицы)
# ============================================================
# Каждый класс здесь = одна таблица в базе данных.
# Поля класса = колонки таблицы.
#
# Пример: класс User создаст таблицу "users" с колонками:
# id, email, username, hashed_password, created_at
#
# relationship() — это связь между таблицами. Например,
# у одного User может быть много Habit'ов (один-ко-многим).
# ============================================================

from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, DateTime, Date, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    Таблица пользователей.
    Хранит данные для авторизации и общую статистику.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- Связи ---
    # Один пользователь -> много привычек
    # back_populates="owner" означает: в модели Habit есть поле owner,
    # которое ссылается обратно на User
    habits = relationship("Habit", back_populates="owner", cascade="all, delete-orphan")


class Habit(Base):
    """
    Таблица привычек.

    Каждая привычка принадлежит одному пользователю (user_id).
    base_xp — сколько XP даётся за выполнение (без множителя).
    icon — эмодзи-иконка привычки (🏃, 📚, 💧 и т.д.)
    """
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    icon = Column(String, default="⭐")
    base_xp = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)  # Можно "выключить" привычку
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- Связи ---
    owner = relationship("User", back_populates="habits")
    completions = relationship(
        "HabitCompletion", back_populates="habit", cascade="all, delete-orphan"
    )


class HabitCompletion(Base):
    """
    Таблица выполнений привычек.

    Каждая запись = "привычка X выполнена в день Y".
    Одна привычка может быть выполнена максимум 1 раз в день.

    xp_earned — сколько XP реально получено (с учётом множителя стрика).
    streak_at_completion — какой был streak на момент выполнения
    (полезно для истории, чтобы потом не пересчитывать).
    """
    __tablename__ = "habit_completions"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    completed_date = Column(Date, nullable=False, default=date.today)
    xp_earned = Column(Integer, nullable=False)
    streak_at_completion = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    # --- Связи ---
    habit = relationship("Habit", back_populates="completions")
