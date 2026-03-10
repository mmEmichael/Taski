import asyncio
import logging
import os
from datetime import datetime, timedelta

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from .config import TG_TOKEN, DATABASE_URL, SERVER_BASE_URL
from .database import SessionLocal
from .models import BotToken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TG_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


async def main():
    logger.info("Starting bot with DB=%s, SERVER_BASE_URL=%s", DATABASE_URL, SERVER_BASE_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())