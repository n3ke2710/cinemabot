import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.dispatcher.router import Router
from aiogram.fsm.storage.memory import MemoryStorage
from config import bot_token, bot, dp, router

import asyncio
from aiogram.filters import Command

from handlers.reqs.tmdb.tmdb import search_movie

logging.basicConfig(level=logging.INFO)


@dp.message(Command('start'))
async def start(message: Message):
    await message.answer("Welcome! Use /find_film to search for a film.")

async def show_film_card(chat_id: int, result) -> None:
    poster_url =f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
    answer_text = f"{result['original title']}\n\n\
    Описание: {result['overview']}\n\n\
    Рейтинг: {result['vote_average']}"
    await bot.send_photo(chat_id=chat_id, photo=poster_url, caption=answer_text)

@dp.message()
async def find_film(message: Message):
	if message.text:
		result = await search_movie(message.text)
		await show_film_card(message.chat.id, result[0])
	else:
		await message.answer("Please provide the film name.")

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())