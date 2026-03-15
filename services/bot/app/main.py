import asyncio
import logging

from redis.asyncio import Redis
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from app.config import TG_TOKEN, DATABASE_URL, SERVER_BASE_URL
from app.handlers.start import router as start_router
from app.handlers.tasks import router as tasks_router
from app.bd__init__ import init_db

redis_client = Redis.from_url("redis://redis_cache:6379/0")
storage = RedisStorage(redis=redis_client)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=TG_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=storage)
dp.include_router(start_router)
dp.include_router(tasks_router)


async def main():
    logger.info("Starting bot with DB=%s, SERVER_BASE_URL=%s", DATABASE_URL, SERVER_BASE_URL)
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())