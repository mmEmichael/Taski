"""API задач — CRUD операции."""
from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Null
from sqlalchemy.orm import Session

from app.schemas.task import TaskCreate, TaskUpdate
from app.database import get_db
from app.api.deps import get_current_user
from app.models.task import TaskStatus
from app.services.task_service import (
    create_task,
    list_tasks,
    get_task_by_id,
    update_task,
    delete_task,
)
from app.services.celery_service import create_celery_task

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/tasks/create")
async def create_task_route(
    data: TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
    token:str = Depends(oauth2_scheme)
):
    """Создание новой задачи."""
    task_id = create_task(db=db, user_id=user_id, data=data)
    #Cоздаем задачу celery
    await create_celery_task(task_id=task_id, due_at=data.due_at, token=token)
    return task_id


@router.get("/tasks")
async def get_task_info_route(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
    status: TaskStatus | None = Query(None),
):
    """Список всех задач."""
    return list_tasks(db=db, user_id=user_id, status=status)


@router.get("/tasks/{id}")
async def get_task_info_route_by_id(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """Получение задачи по ID."""
    return get_task_by_id(db=db, user_id=user_id, task_id=id)


@router.patch("/tasks")
async def update_task_route(
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """Частичное обновление задачи."""
    return update_task(db=db, user_id=user_id, data=data)


@router.delete("/tasks/{id}")
async def delete_task_route(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """Удаление задачи."""
    return delete_task(db=db, user_id=user_id, task_id=id)