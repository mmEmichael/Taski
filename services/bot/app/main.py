import asyncio
import logging
import os
from datetime import datetime, timedelta

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message

from .config import TG_TOKEN, DATABASE_URL, SERVER_BASE_URL
from .database import SessionLocal
from .models import BotToken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=TG_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def register_and_auth_user_on_server(
    tg_id: int,
    username: str | None = None
    ) -> str:
    """
    Регистрирует пользователя на сервере (если нужно) и логинит его.
    Возвращает JWT-токен сервера.
    Здесь пример через существующие /user/register и /user/auth.
    """
    password = f"tg_{tg_id}"

    async with httpx.AsyncClient(base_url=SERVER_BASE_URL, timeout=10.0) as client:
        try:
            await client.post(
                "/user/register",
                json={
                    "username": username or f"tg_{tg_id}",
                    "password": password,
                    "tg_id": tg_id,
                },
            )
        except httpx.HTTPStatusError as exc:
            # Например, 400 / 409 — пользователь уже существует; это не фатально
            logger.warning("Register failed (maybe user exists): %s", exc)

        resp = await client.post(
            "/user/auth",
            json={
                "username": username or f"tg_{tg_id}",
                "password": password,
                "tg_id": tg_id,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        # у вас сервер сейчас возвращает {"token": token}
        return data["token"]


# DEBUG: test start
@dp.message(CommandStart())
async def handle_start(message: Message):
    """
    /start — регистрирует/логинит пользователя на сервере и сохраняет токен.
    """
    tg_id = message.from_user.id
    username = message.from_user.username

    token = await register_and_auth_user_on_server(tg_id=tg_id, username=username)    
    logger.info("Token from server %s", token)


async def main():
    logger.info("Starting bot with DB=%s, SERVER_BASE_URL=%s", DATABASE_URL, SERVER_BASE_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())