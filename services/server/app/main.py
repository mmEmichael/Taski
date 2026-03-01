"""FastAPI приложение — точка входа в приложение."""
from fastapi import FastAPI
from app.database import engine
from app.models import Base

from .api.routes import user, task

# Создание таблиц БД при старте
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(task.router)


@app.get("/")
def read_root():
    """Корневой эндпоинт — проверка работоспособности."""
    return {"message": "Hello, World!"}