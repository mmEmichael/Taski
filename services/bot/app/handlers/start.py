import logging

import httpx
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.config import SERVER_BASE_URL
from app.database import SessionLocal
from app.services.session_service import save_token
from app.keyboards.tasks import create_task_kb

router = Router()
logger = logging.getLogger(__name__)

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
        #сервер возвращает {"token": token}
        return data["token"]


# DEBUG: test start
@router.message(CommandStart())
async def handle_start(message: Message):
    """
    /start — регистрирует/логинит пользователя на сервере и сохраняет токен.
    """
    tg_id = message.from_user.id
    username = message.from_user.username

    token = await register_and_auth_user_on_server(tg_id=tg_id, username=username)


    db = SessionLocal()
    try:
        save_token(db=db, tg_id=tg_id, token=token)
    finally:
        db.close()
        
    logger.info("Token from server %s", token)
    await message.answer(
        f"Привет @{username}!",
        reply_markup=create_task_kb,
    )