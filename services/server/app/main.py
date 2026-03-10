"""FastAPI приложение — точка входа в приложение."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine
from app.models import Base
import asyncio
import logging

from .api.routes import user, task


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    # Создание таблиц БД при старте
    def init_db():
        Base.metadata.create_all(bind=engine)

    logger.info("Инициализация БД (создание таблиц, если их нет).")
    await asyncio.to_thread(init_db)  # Запускаем в отдельном потоке
    # TODO: тут же можно запустить планировщик напоминаний / воркер, если он будет

    logger.info("Приложение FastAPI успешно запущено.")
    yield
    # --- shutdown ---
    logger.info("Остановка приложения FastAPI. Освобождение ресурсов БД.")
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