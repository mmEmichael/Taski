from datetime import datetime
from zoneinfo import ZoneInfo

from celery import Celery

app = Celery('tasks', 
             broker='redis://redis:6379/0',
             backend='redis://redis:6379/0')

APP_TIMEZONE = "Europe/Moscow"
app.conf.timezone = APP_TIMEZONE
app.conf.enable_utc = True

TASK_NAME = "app.services.celery.celery_service.retun_scheduled_task_id"
async def create_celery_task(task_id: int, due_at: datetime, token: str):
    if due_at is not None:
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=ZoneInfo(APP_TIMEZONE))

        app.send_task(
            TASK_NAME,
            args=[task_id, token],
            eta=due_at,
        )
        return "Scheduled task created"
