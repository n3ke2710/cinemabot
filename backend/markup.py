from aiogram import Bot, Dispatcher, types  # type: ignore
from aiogram.filters import Command  # type: ignore
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

import sqlite3
import os

async def get_card_keyboard(message: types.Message, title: str):
    buttons =[]
    buttons.append(types.InlineKeyboardButton(text='Смотреть', callback_data=f"watch_{title}"))
    buttons.append(types.InlineKeyboardButton(text='Еще', callback_data=f"more"))
    keyboard = InlineKeyboardBuilder()
    for button in buttons:
        keyboard.add(button)

    keyboard.adjust(1)
    return keyboard

async def get_movie_keyboard(message: types.Message, ignore = None):
    db_path = f"./backend/temp/{message.chat.id}/movies.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Извлечение данных из базы данных
    cursor.execute('SELECT title, year FROM movies')
    results = cursor.fetchall()
    conn.close()
    buttons = []
    end = 6
    if ignore is None:
        end = 5
    for movie in results[0:end]:
        if movie[0] == ignore:
            continue
        buttons.append(types.InlineKeyboardButton(text=movie[0], 
                                           callback_data=f"movie_{movie[0]}"))
    keyboard = InlineKeyboardBuilder()
    for button in buttons:
        keyboard.add(button)

    keyboard.adjust(1)
    return keyboard
    