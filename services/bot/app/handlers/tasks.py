import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.services.session_service import get_db_and_token
from app.services.api.tasks_api_client import api_create_task, api_get_task_list, api_delete_task
from app.handlers.start import create_task_kb

router = Router()
logger = logging.getLogger(__name__)

# //////////////////////////////////////////////////////////////////
# Create tasks
# //////////////////////////////////////////////////////////////////


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
    Принимаем описание, создаём задачу на сервере и завершаем сценарий.
    """
    description_raw = (message.text or "").strip()
    description = None if description_raw == "-" else description_raw

    data = await state.get_data()
    title = data["title"]
    token = data["access_token"]

    if not await api_create_task(token, title, description):
        await message.answer("Failed to create task on server")

    await state.clear()

    # task — это то, что вернёт /tasks/create (id, title и т.п.)
    await message.answer(
        f"Задача создана ✅\nНазвание: {title}",
        reply_markup=create_task_kb
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


def delete_task_inline_kb(task_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Удалить🗑️",
                    callback_data=f"delete_task:{task_id}",
                )
            ]
        ]
    )


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