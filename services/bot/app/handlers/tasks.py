import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from app.services.session_service import get_db_and_token
from app.keyboards.tasks import create_task_kb, delete_task_inline_kb, cancel_kb
from app.services.api.tasks_api_client import api_create_task, api_get_task_list, api_delete_task, api_get_task_info

router = Router()
logger = logging.getLogger(__name__)

# //////////////////////////////////////////////////////////////////
# Create tasks
# //////////////////////////////////////////////////////////////////


class CreateTaskStates(StatesGroup):
    title = State()
    description = State()
    due_at = State()

@router.message(Command("newtask"))
@router.message(F.text == "Создать задачу")
async def cmd_create_task(message: Message, state: FSMContext):
    """
    Старт создания задачи: проверяем токен, спрашиваем заголовок.
    """
    tg_id = message.from_user.id

    token = await get_db_and_token(tg_id=tg_id, event=message)

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
    Принимаем описание и переходим к шагу ввода времени напоминания.
    """
    description_raw = (message.text or "").strip()
    description = None if description_raw == "-" else description_raw

    data = await state.get_data()
    title = data["title"]
    await state.update_data(description=description)
    await state.set_state(CreateTaskStates.due_at)
    await message.answer(
        "Введите время напоминания в формате `YYYY-MM-DD HH:MM`.\n"
        "Можно указать `-`, если напоминание не нужно.",
        reply_markup=cancel_kb,
    )

@router.message(CreateTaskStates.due_at)
async def process_due_at(message: Message, state: FSMContext):
    """
    Принимаем время напоминания (due_at), создаём задачу и завершаем сценарий.
    """
    due_at_raw = (message.text or "").strip()
    if due_at_raw in {"", "-"}:
        due_at = None
    else:
        try:
            # datetime.fromisoformat принимает и формат с пробелом между датой и временем.
            dt = datetime.fromisoformat(due_at_raw)
            due_at = dt.isoformat(timespec="seconds")
        except ValueError:
            await message.answer(
                "Не понял формат времени. Используйте `YYYY-MM-DD HH:MM` (например, `2026-03-23 18:30`)."
            )
            return

    data = await state.get_data()
    title = data["title"]
    description = data.get("description")
    token = data["access_token"]

    if not await api_create_task(token, title, description, due_at=due_at):
        await message.answer("Failed to create task on server")
        return

    await state.clear()
    reminder_part = f"\nНапоминание: {due_at}" if due_at is not None else "\nНапоминание: не задано"
    await message.answer(
        f"Задача создана ✅\nНазвание: {title}{reminder_part}",
        reply_markup=create_task_kb,
    )


@router.callback_query(F.data == "cancel_create_task")
async def cmd_cancel_create_task(callback: CallbackQuery, state: FSMContext):
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
async def cmd_tasks_list(message: Message):
    """
    Выводим список всех задач
    """
    tg_id = message.from_user.id

    token = await get_db_and_token(tg_id=tg_id, event=message)

    tasks = await api_get_task_list(token)
    if tasks is None:
        await message.answer("Failed to get tasks list")
        return

    for task in tasks:
        task_id = task["id"]
        task_title = task["title"]
        await message.answer(
            f"ID: {task_id}| {task_title}",
            reply_markup=delete_task_inline_kb(task_id)
            )


# //////////////////////////////////////////////////////////////////
# DELETE Task
# //////////////////////////////////////////////////////////////////


@router.callback_query(F.data.startswith("delete_task:"))
async def cmd_delete_task(callback: CallbackQuery):
    tg_id = callback.from_user.id

    token = await get_db_and_token(tg_id=tg_id, event=callback)

    # парсим id задачи из callback_data
    _, task_id_str = callback.data.split(":", 1)
    task_id = int(task_id_str)

    if not await api_delete_task(token, task_id):
        await callback.answer("Failed to delete task %s", task_id)

    # визуально обновляем сообщение
    await callback.message.edit_text(f"Задача {task_id} удалена ✅")
    await callback.answer("Задача удалена.")


# //////////////////////////////////////////////////////////////////
# Get task info
# //////////////////////////////////////////////////////////////////


@router.callback_query(F.data.startswith("task_info:"))
async def cmd_get_task_info(callback: CallbackQuery):
    tg_id = callback.from_user.id

    token = await get_db_and_token(tg_id=tg_id, event=callback)

    # парсим id задачи из callback_data
    _, task_id_str = callback.data.split(":", 1)
    task_id = int(task_id_str)

    task = await api_get_task_info(token, task_id)
    if task is None:
        await callback.answer("Failed to get tasks list")
        return

    task_title = task["title"]
    task_description = task["description"]
    task_status = task["status"]
    task_due_at = task["due_at"]

    # визуально обновляем сообщение
    #await callback.message.edit_text(f"{task_title}\n{task_description}\n{task_status}\n{task_due_at}")
    await callback.message.answer(f"{task_title}\n{task_description}\n{task_status}\n{task_due_at}")