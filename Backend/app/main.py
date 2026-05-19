# ============================================================
# main.py — Точка входа приложения
# ============================================================
# Это главный файл. Здесь мы:
# 1. Создаём FastAPI-приложение
# 2. Настраиваем CORS (чтобы React-фронт мог обращаться к API)
# 3. Подключаем все роутеры
# 4. Создаём таблицы в базе данных
#
# Запуск: uvicorn app.main:app --reload
# --reload означает: перезапускать сервер при изменении кода
#
# После запуска открой http://localhost:8000/docs
# Там будет интерактивная документация Swagger — можно тестировать
# все эндпоинты прямо в браузере!
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth_router, habits, completions, stats

# Создаём приложение
app = FastAPI(
    title="Habit Quest API",
    description="API для трекера привычек с геймификацией",
    version="1.0.0",
)

# ─── CORS (Cross-Origin Resource Sharing) ───
# Браузер блокирует запросы между разными доменами по умолчанию.
# React работает на localhost:3000, API на localhost:8000 —
# это "разные источники" (origins).
# Без CORS настройки фронтенд не сможет общаться с бекендом.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # React dev server
        "http://localhost:5173",     # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # Разрешаем все HTTP-методы (GET, POST, PUT, DELETE)
    allow_headers=["*"],   # Разрешаем все заголовки (включая Authorization)
)

# ─── Подключаем роутеры ───
# Каждый роутер добавляет свои эндпоинты к приложению.
# include_router() — как "прикрутить модуль" к приложению.
app.include_router(auth_router.router)      # /auth/register, /auth/login
app.include_router(habits.router)           # /habits/...
app.include_router(completions.router)      # /completions/...
app.include_router(stats.router)            # /stats, /profile


# ─── Создаём таблицы ───
# Base.metadata.create_all() проверяет какие таблицы уже есть в базе
# и создаёт недостающие. Если таблица уже существует — не трогает.
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    """
    Корневой эндпоинт — просто проверка что сервер работает.

    GET http://localhost:8000/
    """
    return {
        "app": "Habit Quest API",
        "version": "1.0.0",
        "docs": "Открой /docs для интерактивной документации",
    }
