"""FastAPI приложение — точка входа в приложение."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine
from app.models import Base
import asyncio

from .api.routes import user, task

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    # Создание таблиц БД при старте
    def init_db():
        Base.metadata.create_all(bind=engine)
    
    await asyncio.to_thread(init_db)  # Запускаем в отдельном потоке
    # TODO: тут же можно запустить планировщик напоминаний / воркер, если он будет

    yield
    # --- shutdown ---
    engine.dispose()  # Закрыть все соединения
    # TODO: остановить планировщик/воркер, если запускали выше
    ...

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(task.router)


@app.get("/")
def read_root():
    """Корневой эндпоинт — проверка работоспособности."""
    return {"message": "Hello, World!"}