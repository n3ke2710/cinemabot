import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from aiogram.fsm.storage.memory import MemoryStorage
from config import bot_token, bot, dp, router
import aiohttp

import asyncio
from aiogram.filters import Command

from handlers.reqs.tmdb.tmdb import search_movie

logging.basicConfig(level=logging.INFO)


@dp.message(Command('start'))
async def start(message: Message):
    await message.answer("Welcome! Use /find_film to search for a film.")

async def show_film_card(chat_id: int, film_data: dict) -> None:
    poster_url = f"https://image.tmdb.org/t/p/w500{film_data['poster_path']}" if film_data.get('poster_path') else None

    rating = film_data.get('vote_average', 0)
    full_stars = int(rating // 2)
    half_star = 1 if (rating / 2 - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    stars = '⭐' * full_stars + '✬' * half_star + '☆' * empty_stars

    answer_text = (
        f"{film_data.get('title', 'Нет названия')}\n\n"
        f"<b>{'Рейтинг:'}</b> {film_data.get('vote_average', 'N/A')} {stars}\n"
        f"<b>{'Звезды:'}</b> {stars}\n"
        f"<b>{'Описание:'}</b> {film_data.get('overview', 'Описание отсутствует')}"
    )

    if poster_url:
        await bot.send_photo(chat_id=chat_id, photo=poster_url, caption=answer_text, parse_mode='HTML')
    else:
        await bot.send_message(chat_id=chat_id, text=answer_text, parse_mode='HTML')

@dp.message()
async def find_film(message: Message):
    if message.text:
        result = await search_movie(message.text)
        await show_film_card(message.chat.id, result['results'][0])
    else:
        await message.answer("Пожалуйста, укажите название фильма.")

async def main():
    await dp.start_polling(bot, skip_updates=True)

async def on_shutdown():
    await aiohttp.ClientSession().close()

if __name__ == '__main__':
    asyncio.run(main())