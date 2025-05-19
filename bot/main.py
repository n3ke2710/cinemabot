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


@dp.message()
async def find_film(message: Message):
	if message.text:
		result = await search_movie(message.text)
		await message.answer(result)
	else:
		await message.answer("Please provide the film name.")

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())