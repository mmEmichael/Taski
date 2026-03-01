"""Схемы для задач — создание и обновление."""
from pydantic import BaseModel


class TaskCreate(BaseModel):
    """Данные для создания задачи."""
    title: str
    description: str | None = None
    status: str | None = None
    due_at: str | None = None


class TaskUpdate(BaseModel):
    """Данные для частичного обновления задачи."""
    id: int
    title: str | None = None
    description: str | None = None
    status: str | None = None
    due_at: str | None = None

