"""Модель задачи — ORM и статусы."""
import enum
from sqlalchemy import ForeignKey, Column, Enum, Integer, String, DateTime, func

from . import Base


class TaskStatus(enum.Enum):
    """Статусы задачи."""
    DONE = 'done'
    CANCELLED = 'cancelled'
    PENDING = 'pending'


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Enum(TaskStatus), nullable=True)
    due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())