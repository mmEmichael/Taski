"""API задач — CRUD операции."""
from fastapi import APIRouter

from app.schemas.task import TaskCreate, TaskUpdate

router = APIRouter()


@router.post("/tasks/create")
async def create_task(data: TaskCreate):
    """Создание новой задачи."""
    return data


@router.get("/tasks")
async def get_task_info():
    """Список всех задач."""
    return 0


@router.get(f"/tasks/{id}")
async def get_task_info(id):
    """Получение задачи по ID."""
    return id


@router.patch(f"/tasks/{id}")
async def update_task(data: TaskUpdate):
    """Частичное обновление задачи."""
    return data


@router.delete(f"/tasks/{id}")
async def delete_task(id):
    """Удаление задачи."""
    return id