import asyncio
from datetime import datetime

from celery import Celery
from celery.app import task

app = Celery('tasks', 
             broker='redis://redis:6379/0',
             backend='redis://redis:6379/0')

@app.task
def retun_scheduled_task_id(task_id: int):
    return task_id