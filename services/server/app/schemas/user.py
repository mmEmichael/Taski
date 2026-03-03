"""Схемы для пользователей — валидация входных данных."""
from pydantic import BaseModel


class UserCredentials(BaseModel):
    """Регистрация/логин: логин, пароль и опциональный Telegram ID."""
    username: str
    password: str
    tg_id: int | None = None