import logging
import asyncio
from typing import Dict

from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import bot, dp
from handlers.reqs.tmdb.tmdb import search_movie, get_top_movies
from handlers.markup.keyboard_markup_constructor import construct_keyboard_markup
from handlers.reqs.search_href.search import search_first_result
from handlers.reqs.hug_chat_reqs.hug_chat_request import (
	search_movie_by_description,
)
from stats.db_config import Stats

stats = Stats()

logging.basicConfig(level=logging.INFO)
is_series_status: Dict[int, bool] = {}


@dp.message(Command("start"))
async def start(message: Message):
	await message.answer("Welcome! Use /switch_mode to search for a series.")


@dp.message(Command("liked_movies"))
async def get_liked(message: Message):
	await message.answer("Fetching your liked movies...")
	user_id = message.chat.id
	liked_movies = stats.watch_liked_movies(user_id)
	if liked_movies:
		await message.answer("Your liked movies:\n" + "\n".join(liked_movies))
	else:
		await message.answer("You have no liked movies.")


@dp.message(Command("switch_mode"))
async def switch_mode(message: Message):
	chat_id = message.chat.id
	is_series_status[chat_id] = not is_series_status.get(chat_id, False)
	mode = "series" if is_series_status[chat_id] else "films"
	antimode = "films" if is_series_status[chat_id] else "series"
	await message.answer(
		f"Switched to {mode} mode. Use /switch_mode to search for a {antimode}."
	)


@dp.message(Command("history"))
async def show_history(message: Message):
	user_id = message.chat.id
	history = stats.get_request_history(user_id)
	if history:
		history_text = "\n".join(
			[f"{timestamp}: {query}" for query, timestamp in history]
		)
		await message.answer(f"Ваши последние запросы:\n\n{history_text}")
	else:
		await message.answer("У вас пока нет запросов.")


@dp.message(Command("top_movies"))
async def top_movies(message: Message):
	movies = await get_top_movies()
	if movies:
		response = "🎥 <b>Топ-10 самых популярных фильмов:</b>\n\n"
		for i, movie in enumerate(movies, start=1):
			response += (
				f"{i}. <b>{movie['title']}</b> "
				f"({movie.get('release_date', 'N/A')})\n"
			)
		await message.answer(response, parse_mode="HTML")
	else:
		await message.answer(
			"Не удалось получить список популярных фильмов. Попробуйте позже."
		)


@dp.message(Command("search_by_description"))
async def search_by_description(message: Message):
	description = message.get_args()
	if not description:
		await message.answer("Пожалуйста, укажите описание фильма после команды.")
		return

	result = await search_movie_by_description(description)
	if result:
		await message.answer(f"🔍 Найденный фильм:\n\n{result}")
	else:
		await message.answer("Не удалось найти фильм по описанию. Попробуйте позже.")


@dp.message(Command("popular_movies"))
async def popular_movies(message: Message):
	top_queries = stats.get_top_queries()
	if top_queries:
		response = "🎥 <b>Самые популярные запросы:</b>\n\n"
		for i, (query, count) in enumerate(top_queries, start=1):
			response += f"{i}. <b>{query}</b> — {count} раз(а)\n"
		await message.answer(response, parse_mode="HTML")
	else:
		await message.answer("Пока нет популярных запросов.")


@dp.message(Command("menu"))
async def menu(message: Message):
	keyboard = InlineKeyboardMarkup()
	keyboard.add(
		InlineKeyboardButton("Популярные фильмы", callback_data="popular_movies")
	)
	await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.callback_query(lambda callback: callback.data == "popular_movies")
async def show_popular_movies(callback_query: types.CallbackQuery):
	top_queries = stats.get_top_queries()
	if top_queries:
		response = "🎥 <b>Самые популярные запросы:</b>\n\n"
		for i, (query, count) in enumerate(top_queries, start=1):
			response += f"{i}. <b>{query}</b> — {count} раз(а)\n"
		await callback_query.message.edit_text(response, parse_mode="HTML")
	else:
		await callback_query.message.edit_text("Пока нет популярных запросов.")


@dp.message(Command("help"))
async def help_command(message: Message):
	help_text = (
		"📖 <b>Доступные команды:</b>\n\n"
		"/start - Начать работу с ботом\n"
		"/help - Показать это сообщение\n"
		"/top_movies - Показать топ-10 самых популярных фильмов\n"
		"/search_by_description <описание> - Найти фильм по описанию\n"
		"/liked_movies - Показать список понравившихся фильмов\n"
		"/switch_mode - Переключить режим поиска (фильмы/сериалы)\n"
		"/history - Показать историю ваших запросов\n"
		"/popular_movies - Показать самые популярные запросы\n"
		"/menu - Показать главное меню с кнопками\n"
	)
	await message.answer(help_text, parse_mode="HTML")


async def show_film_card(
	chat_id: int, film_data: dict, is_series: bool = False
) -> None:
	poster_url = (
		f"https://image.tmdb.org/t/p/w500{film_data['poster_path']}"
		if film_data.get("poster_path")
		else None
	)

	rating = film_data.get("vote_average", 0)
	full_stars = int(rating // 2)
	half_star = 1 if (rating / 2 - full_stars) >= 0.5 else 0
	empty_stars = 5 - full_stars - half_star
	stars = "⭐" * full_stars + "💫" * half_star + "☆" * empty_stars

	watch_link = search_first_result(
		film_data.get("title" if not is_series else "name", ""),
		is_series=is_series_status.get(chat_id, False),
	)
	answer_text = (
		f"🎬 <b>{film_data.get('title' if not is_series else 'name', 'N/A')}</b>\n\n"
		f"⭐ <b>Rating:</b> {film_data.get('vote_average', 'N/A')} {stars}\n"
		f"📅 <b>Date:</b> {film_data.get('release_date' if not is_series else 'first_air_date', 'N/A')}\n"
		f"----------------------------------------------\n"
		f"\n"
		f"📝 <b>Description:</b> {film_data.get('overview', 'N/A')}\n"
		f"----------------------------------------------\n"
		f'🔗 <b>Watch now:</b> <a href="{watch_link}">Click here to watch</a>'
	)

	if poster_url:
		await bot.send_photo(
			chat_id=chat_id,
			photo=poster_url,
			caption=answer_text,
			parse_mode="HTML",
			reply_markup=construct_keyboard_markup(),
		)
	else:
		await bot.send_message(chat_id=chat_id, text=answer_text, parse_mode="HTML")


@dp.message(lambda message: message.text in ["⏭", "❤️", "🎥"])
async def handle_movie_actions(message: Message):
	if message.text == "❤️":
		user_id = message.chat.id
		movie_title = "Unknown"
		if message.reply_to_message:
			if message.reply_to_message.caption:
				movie_title = message.reply_to_message.caption.split("\n")[0]
			elif message.reply_to_message.text:
				movie_title = message.reply_to_message.text.split("\n")[0]
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
		stats.save_request(user_id, query)
		result = await search_movie(
			query, is_series=is_series_status.get(user_id, False)
		)
		if result and result.get("results"):
			await show_film_card(
				user_id,
				result["results"][0],
				is_series=is_series_status.get(user_id, False),
			)
		else:
			await message.answer("Фильм не найден. Попробуйте другой запрос.")
	else:
		await message.answer("Пожалуйста, укажите название фильма.")


@dp.errors_handler()
async def handle_errors(update, exception):
	logging.error(f"Ошибка: {exception}")
	return True


async def main():
	await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
	asyncio.run(main())
