# ============================================================
# auth.py — Авторизация (JWT + хеширование паролей)
# ============================================================
# КАК РАБОТАЕТ АВТОРИЗАЦИЯ:
#
# 1. Пользователь регистрируется → пароль хешируется и сохраняется в БД.
#    Хеширование — это односторонняя функция: "password123" → "$2b$12$xyz..."
#    Из хеша нельзя восстановить пароль, но можно проверить совпадение.
#
# 2. Пользователь логинится → сервер проверяет пароль и выдаёт JWT-токен.
#    JWT (JSON Web Token) — это зашифрованная строка с данными:
#    {"sub": "user@email.com", "exp": 1234567890}
#    Токен подписан секретным ключом, подделать его нельзя.
#
# 3. Все следующие запросы → клиент отправляет токен в заголовке:
#    Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
#    Сервер расшифровывает токен и знает кто делает запрос.
# ============================================================

from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

# ─── Настройки ───

# SECRET_KEY — секретный ключ для подписи JWT.
# В продакшене НИКОГДА не храни его в коде! Используй переменные окружения.
# Здесь для простоты обучения оставим так.
SECRET_KEY = "your-super-secret-key-change-in-production-please"
ALGORITHM = "HS256"                     # Алгоритм шифрования
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24   # Токен живёт 24 часа

# pwd_context — объект для хеширования паролей.
# bcrypt — один из самых надёжных алгоритмов хеширования.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хеширует пароль.

    "password123" → "$2b$12$LJ3m4ys..." (каждый раз разный хеш!)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет совпадает ли введённый пароль с хешем.

    verify_password("password123", "$2b$12$LJ3m4ys...") → True
    verify_password("wrong",       "$2b$12$LJ3m4ys...") → False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Создаёт JWT-токен.

    Аргументы:
        data: данные для токена, обычно {"sub": "user@email.com"}

    Возвращает:
        str: JWT-токен ("eyJhbGciOiJIUzI1NiIs...")
    """
    to_encode = data.copy()
    # Добавляем время жизни токена
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # jwt.encode() создаёт подписанный токен
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> str | None:
    """
    Расшифровывает JWT-токен и возвращает email пользователя.

    Если токен невалидный или просрочен → возвращает None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        return email
    except JWTError:
        return None
