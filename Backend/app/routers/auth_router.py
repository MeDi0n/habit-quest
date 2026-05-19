# ============================================================
# routers/auth.py — Регистрация и вход
# ============================================================
# Два эндпоинта:
#   POST /auth/register — создать аккаунт
#   POST /auth/login    — войти и получить JWT-токен
#
# Router (роутер) — это способ группировки эндпоинтов.
# Все эндпоинты в этом файле будут иметь префикс /auth.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, Token, UserResponse
from app.auth import hash_password, verify_password, create_access_token

# prefix="/auth" — все пути в этом роутере начинаются с /auth
# tags=["Auth"] — группировка в Swagger-документации
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя.

    POST /auth/register
    Body: {"email": "user@mail.com", "username": "ivan", "password": "123456"}

    Что происходит:
    1. Проверяем, не занят ли email или username
    2. Хешируем пароль (никогда не храним пароль открытым текстом!)
    3. Создаём пользователя в базе
    4. Возвращаем данные пользователя (без пароля)
    """
    # Проверяем email
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот email уже зарегистрирован",
        )

    # Проверяем username
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Это имя пользователя уже занято",
        )

    # Создаём пользователя
    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(user)      # Добавляем в сессию
    db.commit()       # Сохраняем в базу
    db.refresh(user)  # Обновляем объект (чтобы получить id)

    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """
    Вход в аккаунт.

    POST /auth/login
    Body: {"email": "user@mail.com", "password": "123456"}

    Что происходит:
    1. Ищем пользователя по email
    2. Проверяем пароль
    3. Если всё ОК — создаём JWT-токен и возвращаем его
    4. Клиент сохраняет токен и отправляет его во всех следующих запросах
    """
    # Ищем пользователя
    user = db.query(User).filter(User.email == data.email).first()

    # Проверяем пароль (используем одну и ту же ошибку для email и пароля,
    # чтобы злоумышленник не мог узнать существует ли email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    # Создаём токен. "sub" (subject) — стандартное поле JWT для идентификации.
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}
