from sqlalchemy import insert
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, user_id: int, data: TaskCreate) -> dict:
    """Создание новой задачи."""
    query = insert(Task).values(
        user_id=user_id,
        title=data.title,
        description=data.description,
        status=data.status,
        due_at=data.due_at,
    )
    db.execute(query)
    db.commit()
    return {"message": "Task created successfully"}


def list_tasks(
    db: Session,
    user_id: int,
    status: TaskStatus | None = None,
) -> list[dict]:
    """Список задач пользователя с опциональным фильтром по статусу.

    Возвращает только id и title для каждой задачи.
    """
    query = db.query(Task).filter(Task.user_id == user_id)

    if status is not None:
        query = query.filter(Task.status == status)

    rows = query.all()
    return [{"id": r.id, "title": r.title} for r in rows]


def get_task_by_id(db: Session, user_id: int, task_id: int) -> Task:
    """Получение одной задачи по ID пользователя и задачи."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def update_task(db: Session, user_id: int, data: TaskUpdate) -> Task:
    """Частичное обновление задачи по данным TaskUpdate."""
    task = db.query(Task).filter(Task.id == data.id, Task.user_id == user_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status
    if data.due_at is not None:
        task.due_at = data.due_at

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, user_id: int, task_id: int) -> dict:
    """Удаление задачи."""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}

