import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv  # type: ignore
from aiogram.dispatcher.router import Router
from aiogram.fsm.storage.memory import MemoryStorage

# Загружаем переменные окружения
load_dotenv()

# Получаем токен из переменных окружения
bot_token = os.getenv('BOT_TOKEN')
if not bot_token:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# Создаём экземпляры бота и диспетчера
bot = Bot(token=bot_token)
dp = Dispatcher()

storage = MemoryStorage()
router = Router()