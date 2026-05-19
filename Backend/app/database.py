# ============================================================
# database.py — Подключение к базе данных
# ============================================================
# SQLAlchemy — это ORM (Object-Relational Mapping).
# Вместо того чтобы писать SQL-запросы руками ("SELECT * FROM habits"),
# ты работаешь с Python-объектами: habit = Habit(name="Running")
#
# SQLite — это файловая база данных. Не нужно ничего устанавливать,
# данные хранятся в одном файле (habit_quest.db).
# Для продакшена обычно используют PostgreSQL, но для обучения SQLite идеален.
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# URL подключения к базе. "sqlite:///./habit_quest.db" означает:
# - sqlite — тип базы данных
# - ./habit_quest.db — файл будет создан в текущей папке
DATABASE_URL = "sqlite:///./habit_quest.db"

# Engine — это "мотор" который управляет подключениями к базе.
# connect_args={"check_same_thread": False} нужен только для SQLite,
# потому что SQLite по умолчанию работает только в одном потоке.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal — это фабрика сессий. Каждая сессия = одно "общение" с базой.
# Когда приходит HTTP-запрос, мы создаём сессию, делаем работу, и закрываем.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base — базовый класс для всех моделей (таблиц).
# Все наши модели (User, Habit и т.д.) будут наследоваться от него.
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Генератор, который создаёт сессию базы данных для каждого запроса.

    Используется как "зависимость" (dependency) в FastAPI:
        @router.get("/habits")
        def get_habits(db: Session = Depends(get_db)):
            ...

    yield — это как return, но после завершения запроса
    код после yield выполнится (db.close()), чтобы закрыть сессию.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
