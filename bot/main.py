import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from aiogram.fsm.storage.memory import MemoryStorage
from config import bot_token, bot, dp, router
import aiohttp

import asyncio
from aiogram.filters import Command
from aiogram import F

from handlers.reqs.tmdb.tmdb import search_movie
from handlers.markup.keyboard_markup_constructor import construct_keyboard_markup
from handlers.reqs.search_href.search import search_first_result
import sqlite3
from stats.db_config import Stats

stats = Stats()

logging.basicConfig(level=logging.INFO)
is_series_status: dict[int, bool] = {}

@dp.message(Command('start'))
async def start(message: Message):
    await message.answer("Welcome! Use /switch_mode to search for a series.")


@dp.message(Command('liked_movies'))
async def get_liked(message: Message):
    await message.answer("Fetching your liked movies...")
    user_id = message.chat.id
    liked_movies = stats.watch_liked_movies(user_id)
    if liked_movies:
        await message.answer("Your liked movies:\n" + "\n".join(liked_movies))
    else:
        await message.answer("You have no liked movies.")

@dp.message(Command('switch_mode'))
async def switch_mode(message: Message):
    chat_id = message.chat.id
    is_series_status[chat_id] = not is_series_status.get(chat_id, False)
    mode = "series" if is_series_status[chat_id] else "films"
    antimode = "films" if is_series_status[chat_id] else "series"
    await message.answer(f"Switched to {mode} mode. Use /switch_mode to search for a {antimode}.")

async def show_film_card(chat_id: int, film_data: dict, is_series: bool = False) -> None:
    poster_url = f"https://image.tmdb.org/t/p/w500{film_data['poster_path']}" if film_data.get('poster_path') else None

    rating = film_data.get('vote_average', 0)
    full_stars = int(rating // 2)
    half_star = 1 if (rating / 2 - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    stars = '⭐' * full_stars + '💫' * half_star + '☆' * empty_stars

    watch_link = search_first_result(film_data.get('title' if not is_series else 'name', ''), is_series=is_series_status.get(chat_id, False))
    answer_text = (
        f"🎬 <b>{film_data.get('title' if not is_series else 'name', 'N/A')}</b>\n\n"
        f"⭐ <b>Rating:</b> {film_data.get('vote_average', 'N/A')} {stars}\n"
        f"📅 <b>Date:</b> {film_data.get('release_date' if not is_series else 'first_air_date', 'N/A')}\n"
        f"----------------------------------------------\n"
        f"\n"
        f"📝 <b>Description:</b> {film_data.get('overview', 'N/A')}\n"
        f"----------------------------------------------\n"
        f"🔗 <b>Watch now:</b> <a href=\"{watch_link}\">Click here to watch</a>"
    )

    if poster_url:
        await bot.send_photo(chat_id=chat_id, photo=poster_url, caption=answer_text, parse_mode='HTML', reply_markup=construct_keyboard_markup())
    else:
        await bot.send_message(chat_id=chat_id, text=answer_text, parse_mode='HTML')


@dp.message(lambda message: message.text in ["⏭", "❤️", "🎥"])
async def handle_movie_actions(message: Message):
    if message.text == "❤️":
        # Save liked movie to user_stats.db
        user_id = message.chat.id
        movie_title = "Unknown"
        if message.reply_to_message:
            if message.reply_to_message.caption:
                movie_title = message.reply_to_message.caption.split('\n')[0]
            elif message.reply_to_message.text:
                movie_title = message.reply_to_message.text.split('\n')[0]

        stats.save_liked_movie(user_id, movie_title)

        await message.answer("You liked the movie!")
    elif message.text == "🎥":
        await message.answer("You want to watch the movie!")
    elif message.text == "⏭":
        await message.answer("You want to skip the movie!")

@dp.message()
async def find_film(message: Message):
    if message.text:
        user_id = message.chat.id
        query = message.text

        # Сохранение запроса в историю
        stats.save_request(user_id, query)

        # Поиск фильма
        result = await search_movie(query, is_series=is_series_status.get(user_id, False))
        if result and result.get('results'):
            await show_film_card(user_id, result['results'][0], is_series=is_series_status.get(user_id, False))
        else:
            await message.answer("Фильм не найден. Попробуйте другой запрос.")
    else:
        await message.answer("Пожалуйста, укажите название фильма.")

async def main():
    await dp.start_polling(bot, skip_updates=True)

async def on_shutdown():
    await aiohttp.ClientSession().close()

if __name__ == '__main__':
    asyncio.run(main())