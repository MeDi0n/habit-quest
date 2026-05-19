# 🎮 Habit Quest — Backend API

Бекенд для трекера привычек с геймификацией.

## Технологии

- **FastAPI** — веб-фреймворк для API
- **SQLAlchemy** — ORM для работы с базой данных
- **SQLite** — база данных (файловая, не требует установки)
- **JWT (python-jose)** — авторизация через токены
- **Pydantic** — валидация данных

## Быстрый старт

```bash
# 1. Установи Python 3.11+ (если ещё нет)
# 2. Создай виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Запусти сервер
uvicorn app.main:app --reload

# 5. Открой документацию
# http://localhost:8000/docs
```

## Структура проекта

```
app/
├── main.py           — Точка входа, FastAPI-приложение
├── database.py       — Подключение к SQLite
├── models.py         — Таблицы базы данных (User, Habit, HabitCompletion)
├── schemas.py        — Pydantic-схемы для валидации JSON
├── auth.py           — JWT-утилиты (хеширование, токены)
├── dependencies.py   — Зависимости (get_current_user)
├── xp_system.py      — Система XP и уровней
└── routers/
    ├── auth_router.py   — POST /auth/register, POST /auth/login
    ├── habits.py        — CRUD /habits/
    ├── completions.py   — POST/DELETE /completions/{id}, GET /completions/today
    └── stats.py         — GET /stats, GET /profile
```

## API Эндпоинты

### Авторизация
| Метод | Путь             | Описание              |
|-------|------------------|-----------------------|
| POST  | /auth/register   | Регистрация           |
| POST  | /auth/login      | Вход (получить токен) |

### Привычки
| Метод  | Путь           | Описание                |
|--------|----------------|-------------------------|
| GET    | /habits/       | Все привычки            |
| POST   | /habits/       | Создать привычку        |
| PATCH  | /habits/{id}   | Обновить привычку       |
| DELETE | /habits/{id}   | Удалить привычку        |

### Выполнение
| Метод  | Путь               | Описание                     |
|--------|--------------------|-----------------------------|
| GET    | /completions/today | Привычки на сегодня со стрик |
| POST   | /completions/{id}  | Отметить выполненной         |
| DELETE | /completions/{id}  | Отменить выполнение          |

### Статистика
| Метод | Путь     | Описание             |
|-------|----------|----------------------|
| GET   | /stats   | Общая статистика     |
| GET   | /profile | Профиль пользователя |

## Система XP

- **Base XP**: каждая привычка имеет базовый XP (5-100)
- **Streak Multiplier**: множитель растёт с каждым днём подряд
  - 1 день: ×1.0
  - 3 дня: ×1.2
  - 6 дней: ×1.5
  - 10+ дней: ×2.0 (максимум)
- **Уровни**: пороги растут с каждым уровнем
  - Level 1: 0 XP, Level 2: 50 XP, Level 3: 150 XP, Level 4: 300 XP...
