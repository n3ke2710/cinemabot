import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем API ключ из переменных окружения
tmdb_api_key = os.getenv('TMDB_API_KEY')
if not tmdb_api_key:
    raise ValueError("TMDB_API_KEY не найден в переменных окружения")

# Базовый URL для API TMDB
base_url = "https://api.themoviedb.org/3/"