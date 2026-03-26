import asyncio
import logging
from celery import Celery
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Импорты ваших модулей
from app.config import TG_TOKEN
from app.models.bot_sessions import BotToken
from app.database import SessionLocal
from app.services.api.tasks_api_client import api_get_task_info

# Настройка логирования для воркера
logger = logging.getLogger(__name__)

# Инициализация Celery
# Обратите внимание: хост 'redis_cache' должен совпадать с именем сервиса в docker-compose
app = Celery('tasks', 
             broker='redis://redis_cache:6379/0',
             backend='redis://redis_cache:6379/0')
app.conf.timezone = "Europe/Moscow"
app.conf.enable_utc = True

# Вспомогательная асинхронная функция для отправки сообщения
async def send_tg_notification(chat_id: int, text: str):
    """
    Создает временный экземпляр бота для отправки сообщения и закрывает сессию.
    Это исключает конфликты с основным циклом бота.
    """
    bot = Bot(
        token=TG_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        logger.info(f"Message sent to {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
    finally:
        # Обязательно закрываем сессию, чтобы не плодить зомби-соединения
        await bot.session.close()

@app.task(name="app.services.celery.celery_service.retun_scheduled_task_id")
def retun_scheduled_task_id(task_id: int, token: str):
    """
    Основная задача Celery для уведомления пользователя.
    """
    # 1. Получаем данные о задаче через API
    try:
        task = asyncio.run(api_get_task_info(token, task_id))
        if not task:
            logger.error("Task info not found or API request failed for task_id=%s", task_id)
            return
        task_title = task.get("title", "Без названия")
        # Можно добавить описание или дедлайн:
        # task_due_at = task.get("due_at")
    except Exception as e:
        logger.error(f"Error fetching task info: {e}")
        return

    # 2. Ищем tg_id в базе данных по токену сервера
    db = SessionLocal()
    tg_id = None
    try:
        session_record = db.query(BotToken).filter(BotToken.server_token == token).one_or_none()
        if session_record:
            tg_id = session_record.tg_id
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        db.close()

    # 3. Если пользователь найден, отправляем сообщение
    if tg_id:
        message_text = f"🔔 <b>Напоминание о задаче</b>\n\n📌 {task_title}"
        
        # Запускаем асинхронную функцию в синхронном контексте воркера
        asyncio.run(send_tg_notification(tg_id, message_text))
    else:
        logger.warning(f"User with token {token[:10]}... not found in DB")
