"""Схемы для пользователей — валидация входных данных."""
from pydantic import BaseModel


class UserCredentials(BaseModel):
    """Регистрация/логин: логин, пароль, Telegram ID."""
    username: str | None = None
    password: str | None = None
    tg_id: int | None = None