"""API задач — CRUD операции."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import insert
from sqlalchemy.orm import Session, query

from app.schemas.task import TaskCreate, TaskUpdate
from app.database import get_db
from app.api.deps import get_current_user
from app.models.task import Task, TaskStatus

router = APIRouter()


@router.post("/tasks/create")
async def create_task(
    data: TaskCreate, 
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_current_user)
    ):
    """Создание новой задачи."""
    query = insert(Task).values(
        user_id=user_id,
        title=data.title,
        description=data.description,
        status=data.status,
        due_at=data.due_at
    )
    db.execute(query)
    db.commit()
    return {"message": "Task created successfully"}
    


@router.get("/tasks")
async def get_task_info(
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_current_user),
    status: TaskStatus | None = Query(None)
    ):
    """Список всех задач."""
    query = db.query(Task).filter(Task.user_id == user_id)

    if status is not None:
        query = query.filter(Task.status == status)

    rows = query.all()
    return [{"id": r.id, "title": r.title} for r in rows]


@router.get("/tasks/{id}")
async def get_task_info(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """Получение задачи по ID."""
    task = db.query(Task).filter(Task.id == id, Task.user_id == user_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks")
async def update_task(
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """Частичное обновление задачи."""
    task = db.query(Task).filter(Task.id == data.id, Task.user_id == user_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Обновляем только те поля, которые переданы
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status
    if data.due_at is not None:
        task.due_at = data.due_at  # при необходимости конвертируй из строки в datetime

    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{id}")
async def delete_task(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """Удаление задачи."""
    task = db.query(Task).filter(Task.id == id, Task.user_id == user_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}