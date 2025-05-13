import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv  # type: ignore
import imdb # type: ignore

# Загружаем переменные окружения
load_dotenv()

# Получаем токен из переменных окружения
token = os.getenv('BOT_TOKEN')
if not token:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

# Создаём экземпляры бота и диспетчера
bot = Bot(token=token)
dp = Dispatcher()

ia = imdb.IMDb()