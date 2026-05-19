# ============================================================
# dependencies.py — Зависимости (Dependencies)
# ============================================================
# В FastAPI "зависимость" — это функция, которая выполняется
# ПЕРЕД обработкой запроса. Например:
#
#   @router.get("/habits")
#   def get_habits(user: User = Depends(get_current_user)):
#       ...
#
# Depends(get_current_user) означает:
# 1. Достань токен из заголовка Authorization
# 2. Расшифруй его
# 3. Найди пользователя в базе
# 4. Если всё ОК — передай его в функцию как аргумент user
# 5. Если что-то не так — верни ошибку 401 (Unauthorized)
#
# Это очень удобно: не нужно в каждом эндпоинте вручную
# проверять авторизацию.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import decode_access_token
from app.models import User

# OAuth2PasswordBearer — говорит FastAPI:
# "Ищи токен в заголовке Authorization: Bearer <token>"
# tokenUrl="auth/login" — URL для получения токена (для документации Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Извлекает текущего пользователя из JWT-токена.

    Цепочка зависимостей:
    HTTP-запрос → oauth2_scheme достаёт токен → decode_access_token
    расшифровывает → ищем пользователя в базе → возвращаем.

    Если на любом этапе что-то не так → HTTPException 401.
    """
    # Стандартная ошибка авторизации
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невалидный токен авторизации",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Пробуем расшифровать токен
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    # Ищем пользователя в базе
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user
