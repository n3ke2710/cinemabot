import os
import asyncio
from collections import defaultdict

from aiogram import types  # type: ignore
from aiogram.filters import Command  # type: ignore
from aiogram import F

from config import bot, dp  # Импортируем bot и dp из config
from films import search, give_result_page

from stats import add_to_history, get_history
from ai.ai_req import query_hugging_chat

import requests

status: defaultdict[int, str] = defaultdict(lambda: 'default')

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я бот созданный с помощью aiogram.')


@dp.message(Command('ai'))
async def cmd_ai(message: types.Message):
    status[message.chat.id] = 'ai'
    await message.answer(
        "Опиши фильм, а я попробую его угадать!\n(Учтите, это может занять некоторое время)"
    )

@dp.message(Command('kp'))
async def cmd_kp(message: types.Message):
	url = "https://api.kinopoisk.dev/v1.4/image?page=1&limit=10"
	headers = {"accept": "application/json"}
	response = requests.get(url, headers=headers)

	print(response.text)

@dp.message(lambda message: message.photo)
async def handle_photo_message(message: types.Message):
    file_path = "backend/stock/azir.mp3"
    if not os.path.exists(file_path):
        await message.answer("Файл не найден. Пожалуйста, проверьте путь.")
        return

    audio_file = types.FSInputFile(file_path)
    await message.answer_audio(audio_file)

@dp.message(Command('history'))
async def view_history(message: types.Message):
    history = await get_history(message.chat.id)
    if not history:
        await message.answer("История пуста.")
    else:
        await message.answer(f"Ваша история:\n{history}")

@dp.message()
async def bot_answer(message: types.Message):
    user_status = status[message.chat.id]
    
    if user_status == 'ai':
        if not isinstance(message.text, str):
            await message.answer('Ошибка: текст сообщения отсутствует.')
            return
        await message.answer('Обрабатываю запрос...')
        response = await query_hugging_chat(message.text)
        await bot.delete_message(message.chat.id, message.message_id + 1)
        await message.answer(response)
        status[message.chat.id] = 'default'
    else:
        await search(message)

@dp.callback_query(F.data.startswith("movie_"))
async def callback_movie(callback: types.CallbackQuery):
    if not isinstance(callback.data, str):
        raise TypeError("callback is not a strng")
    movie = callback.data.split("_")[1]
    if not isinstance(callback.message, types.Message):
        raise TypeError("callback message is wrong")
    await give_result_page(callback.message, movie)
    await add_to_history(id=callback.message.chat.id, movie=movie)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
