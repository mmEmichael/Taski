import logging

import httpx

from app.config import SERVER_BASE_URL

logger = logging.getLogger(__name__)

async def api_create_task(
        token: str,
        title: str,
        description: str | None,
        due_at: str | None = None,
) -> bool:
    """
    Запрос на создание задачи на сервере
    """
    try:
        async with httpx.AsyncClient(base_url=SERVER_BASE_URL, timeout=10.0) as client:
            payload = {
                "title": title,
                "description": description,
            }
            if due_at is not None:
                payload["due_at"] = due_at

            resp = await client.post(
                "/tasks/create",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.exception("Failed to create task on server")
        return False
    
    return True

async def api_get_task_list(token: str):
    """
    Запрос списка задач c сервера
    """
    try:
        async with httpx.AsyncClient(base_url=SERVER_BASE_URL, timeout=10.0) as client:
            resp = await client.get(
                "/tasks",
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            tasks = resp.json()
    except httpx.HTTPError as exc:
        logger.exception("Failed to get tasks list")
        return None
    
    return tasks

async def api_delete_task(
    token: str,
    task_id: int
) -> bool:
    """
    Удаление задач c сервера
    """
    try:
        async with httpx.AsyncClient(base_url=SERVER_BASE_URL, timeout=10.0) as client:
            resp = await client.delete(
                f"/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.exception("Failed to delete task %s", task_id)
        return False
    
    return True

async def api_get_task_info(
        token: str,
        task_id: int
):
    """
    Запрос информации о задаче по id задач c сервера
    """
    try:
        async with httpx.AsyncClient(base_url=SERVER_BASE_URL, timeout=10.0) as client:
            resp = await client.get(
                f"/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            task = resp.json()
    except httpx.HTTPError as exc:
        logger.exception("Failed to delete task %s", task_id)
        return None
    
    return task