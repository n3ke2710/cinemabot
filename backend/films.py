import os
import asyncio

from aiogram import Bot, Dispatcher, types  # type: ignore
from aiogram.filters import Command  # type: ignore
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

import sqlite3

from dotenv import load_dotenv  # type: ignore
import imdb  # type: ignore
from icrawler.builtin import GoogleImageCrawler # type: ignore
from config import ia, bot  # Импортируем ia и bot из config
from markup import get_movie_keyboard, get_card_keyboard

async def search(message: types.Message, text=None, shift=0):
    await message.answer('Обрабатываю запрос...')
    if text is None:
        text = message.text
    query = text  # Извлекаем текст сообщения
    if not query:
        await bot.delete_message(message.chat.id, message.message_id + 1)
        await message.answer("Пожалуйста, введите название фильма.")
        return

    # Поиск фильма
    results = ia.search_movie(query)
	
   
    # Сохранение результатов поиска в базу данных
    if not isinstance(message.chat.id, int):
        raise TypeError("Chat id is not integer")
    db_path = f"./backend/temp/{message.chat.id}/movies.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Создаем директорию, если ее нет
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаем таблицу, если она не существует
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year TEXT,
            imdb_id TEXT UNIQUE
        )
    ''')

    # Сохраняем результаты поиска
    for movie in results[:5]:
        title = movie.get('title', '')
        year = movie.get('year', '')
        imdb_id = movie.movieID
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO movies (title, year, imdb_id)
                VALUES (?, ?, ?)
            ''', (title, year, imdb_id))
        except sqlite3.Error as e:
            print(f"Ошибка при сохранении фильма {title}: {e}")

    conn.commit()
    conn.close()

    builder = await get_card_keyboard(message, title=results[0].get('title', ''))
    await bot.delete_message(message.chat.id, message.message_id + 1)
    if results:
        builder.adjust(1)  # Настраиваем клавиатуру
        await give_result_page(message, title=results[0].get('title', ''))
    else:
        await message.answer("К сожалению, я ничего не нашел по вашему запросу.")


async def give_result_page(message: types.Message, title: str):
    db_path = f"./backend/temp/{message.chat.id}/movies.db"
    if not os.path.exists(db_path):
        await message.answer("База данных с результатами поиска не найдена.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ищем фильм по названию
    cursor.execute('''
        SELECT title, year, imdb_id FROM movies WHERE title LIKE ?
    ''', (f"%{title}%",))
    results_title = cursor.fetchall()
    conn.close()

    if results_title:
        response = ""
        result = results_title[0]
        movie_title, year, imdb_id = result
        response += f"🎬 {movie_title} ({year})\nIMDB: https://www.imdb.com/title/tt{imdb_id}/\n\n"
		
        builder = await get_card_keyboard(message, title=movie_title)
        builder.adjust(1)

        await message.answer(response, reply_markup=builder.as_markup(), disable_web_page_preview=False)
    else:
        await message.answer("К сожалению, я ничего не нашел по вашему запросу.")