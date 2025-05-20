import os
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv  # type: ignore
from aiogram.dispatcher.router import Router
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Загружаем переменные окружения
    load_dotenv()

    # Получаем токен из переменных окружения
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        raise ValueError("BOT_TOKEN не найден в переменных окружения")

    # Создаём экземпляры бота и диспетчера
    bot = Bot(token=bot_token, parse_mode="HTML")
    dp = Dispatcher()
    storage = MemoryStorage()
    router = Router()

except Exception as e:
    logger.error(f"Ошибка при инициализации бота: {e}")
    raise