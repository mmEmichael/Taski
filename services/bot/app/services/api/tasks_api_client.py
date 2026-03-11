import logging

import httpx

from app.config import SERVER_BASE_URL

logger = logging.getLogger(__name__)

async def api_create_task(
        token: int,
        title: str,
        description: str
) -> bool:
    """
    Запрос на создание задачи на сервере
    """
    try:
        async with httpx.AsyncClient(base_url=SERVER_BASE_URL, timeout=10.0) as client:
            resp = await client.post(
                "/tasks/create",
                json={
                    "title": title,
                    "description": description,
                    # status и due_at пока не задаём — сервер их считает опциональными
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        logger.exception("Failed to create task on server")
        return False
    
    return True

async def api_get_task_list(token: int):
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
    token: int,
    task_id: int
) -> bool:
    """
    Запрос списка задач c сервера
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