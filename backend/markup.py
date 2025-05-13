from aiogram import Bot, Dispatcher, types  # type: ignore
from aiogram.filters import Command  # type: ignore
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

import sqlite3
import os

async def get_movie_keyboard(message: types.Message, shift=0):
    db_path = f"./backend/temp/{message.chat.id}/movies.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()


    shift_path = f"./backend/temp/{message.chat.id}/shift.txt"
    if not os.path.exists(shift_path):
        with open(shift_path, 'w') as shift_file:
            shift_file.write('0')

    with open(shift_path, 'r') as shift_file:
        shift += int(shift_file.read().strip())

    # Извлечение данных из базы данных
    cursor.execute('SELECT title, year FROM movies')
    results = cursor.fetchall()
    conn.close()
    buttons = []
    for movie in results[shift : shift+5]:
        buttons.append(types.InlineKeyboardButton(text=movie[0], 
                                           callback_data=f"movie_{movie[0]}"))
    keyboard = InlineKeyboardBuilder()
    for button in buttons:
        keyboard.add(button)

    keyboard.adjust(1)
    return keyboard
    