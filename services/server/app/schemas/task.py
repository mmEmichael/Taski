"""Схемы для задач — создание и обновление."""
from datetime import datetime

from pydantic import BaseModel

from app.models.task import TaskStatus

class TaskCreate(BaseModel):
    """Данные для создания задачи."""
    title: str
    description: str | None = None
    status: TaskStatus | None = None
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    """Данные для частичного обновления задачи."""
    id: int
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    due_at: datetime | None = None

