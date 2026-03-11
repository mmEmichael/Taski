import logging

import httpx
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from app.config import SERVER_BASE_URL
from app.database import SessionLocal
from app.services.session_service import get_valid_token
from app.handlers.start import create_task_kb

router = Router()
logger = logging.getLogger(__name__)

# //////////////////////////////////////////////////////////////////
# Create tasks
# //////////////////////////////////////////////////////////////////

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="cancel_create_task")]
    ]
)

class CreateTaskStates(StatesGroup):
    title = State()
    description = State()


@router.message(Command("newtask"))
@router.message(F.text == "Создать задачу")
async def cmd_new_task(message: Message, state: FSMContext):
    """
    Старт создания задачи: проверяем токен, спрашиваем заголовок.
    """
    tg_id = message.from_user.id

    db = SessionLocal()
    try:
        token = get_valid_token(db, tg_id)
    finally:
        db.close()

    if not token:
        await message.answer("Сначала авторизуйтесь через /start, чтобы я связался с сервером.")
        return

    # Сохраняем токен в FSM-контексте, чтобы не лезть в БД на каждом шаге
    await state.update_data(access_token=token)
    await state.set_state(CreateTaskStates.title)
    await message.answer("Начинаем создание задачи…", reply_markup=ReplyKeyboardRemove())
    await message.answer("Введите заголовок задачи.", reply_markup=cancel_kb)


@router.message(CreateTaskStates.title)
async def process_title(message: Message, state: FSMContext):
    """
    Принимаем заголовок и переходим к описанию.
    """
    title = (message.text or "").strip()
    if not title:
        await message.answer("Заголовок не может быть пустым. Введите заголовок задачи.")
        return

    await state.update_data(title=title)
    await state.set_state(CreateTaskStates.description)
    await message.answer(
        "Введите описание задачи (или отправьте '-' чтобы оставить без описания).",
        reply_markup=cancel_kb
    )


@router.message(CreateTaskStates.description)
async def process_description(message: Message, state: FSMContext):
    """
    Принимаем описание, создаём задачу на сервере и завершаем сценарий.
    """
    description_raw = (message.text or "").strip()
    description = None if description_raw == "-" else description_raw

    data = await state.get_data()
    title = data["title"]
    token = data["access_token"]

    try:
        async with httpx.AsyncClient(base_url=SERVER_BASE_URL, timeout=10.0) as client:
            resp = await client.post(
                "/tasks/create",
                json={
                    "title": title,
                    "description": description,
                    # status и due_at пока не задаём — сервер их считает опциональными
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            task = resp.json()
    except httpx.HTTPError as exc:
        logger.exception("Failed to create task on server")
        await state.clear()
        await message.answer(f"Не удалось создать задачу: {exc}")
        return

    await state.clear()

    # task — это то, что вернёт /tasks/create (id, title и т.п.)
    await message.answer(
        f"Задача создана ✅\nНазвание: {title}",
        reply_markup=create_task_kb
        )


@router.callback_query(F.data == "cancel_create_task")
async def cancel_create_task(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_reply_markup()  # убрать кнопки под последним сообщением
    await callback.message.answer(
        "Создание задачи отменено.",
        reply_markup=create_task_kb
        )
    await callback.answer()  # закрыть "часики" у кнопки


# //////////////////////////////////////////////////////////////////
# Tasks list
# //////////////////////////////////////////////////////////////////

@router.message(Command("taskslist"))
@router.message(F.text == "Задачи")
async def cmd_new_task(message: Message):
    """
    Выводим список всех задач
    """
    tg_id = message.from_user.id

    db = SessionLocal()
    try:
        token = get_valid_token(db, tg_id)
    finally:
        db.close()

    if not token:
        await message.answer("Сначала авторизуйтесь через /start, чтобы я связался с сервером.")
        return

    try:
        async with httpx.AsyncClient(base_url=SERVER_BASE_URL, timeout=10.0) as client:
            resp = await client.get(
                "/tasks",
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            tasks = resp.json()
    except httpx.HTTPError as exc:
        logger.exception("Failed to get tasks list")
        await message.answer(f"Не удалось получить список задач: {exc}")
        return

    for task in tasks:
        task_id = task["id"]
        task_title = task["title"]
        await message.answer(f"ID: {task_id}| {task_title}")