import enum
from sqlalchemy import Column, Enum, Integer, BigInteger, String, DateTime, func

from . import Base

class TaskStatus(enum.Enum):
    DONE = 'done'
    CANCELLED = 'cancelled'
    PENDING = 'pending'

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(Enum(TaskStatus), nullable=True)
    due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())