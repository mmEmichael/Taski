"""FastAPI приложение — точка входа в приложение."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine
from app.models import Base

from .api.routes import user, task

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    
    # Создание таблиц БД при старте
    Base.metadata.create_all(bind=engine)
    # TODO: тут же можно запустить планировщик напоминаний / воркер, если он будет

    yield
    # --- shutdown ---
    # TODO: остановить планировщик/воркер, если запускали выше
    ...

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(task.router)


@app.get("/")
def read_root():
    """Корневой эндпоинт — проверка работоспособности."""
    return {"message": "Hello, World!"}