import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import TG_TOKEN, DATABASE_URL, SERVER_BASE_URL
from app.handlers.start import router as start_router
from app.handlers.tasks import router as tasks_router
from app.bd__init__ import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=TG_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start_router)
dp.include_router(tasks_router)


async def main():
    logger.info("Starting bot with DB=%s, SERVER_BASE_URL=%s", DATABASE_URL, SERVER_BASE_URL)
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())