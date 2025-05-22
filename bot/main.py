import logging
import asyncio
import signal
from typing import Dict, Any

from aiogram import types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Update, ErrorEvent
from aiogram.filters import Command

from config import bot, dp
from handlers.reqs.tmdb.tmdb import search_movie, get_top_movies
from handlers.markup.keyboard_markup_constructor import (
	construct_keyboard_markup
)
from handlers.reqs.search_href.search import search_first_result
from handlers.reqs.hug_chat_reqs.hug_chat_request import (
	search_movie_by_description,
)
from stats.db_config import Stats

# Настройка логирования
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

stats = Stats()
is_series_status: Dict[int, bool] = {}

# Флаг для корректного завершения работы
is_running = True

def signal_handler(signum, frame):
	"""Обработчик сигналов для корректного завершения работы"""
	global is_running
	logger.info("Получен сигнал завершения работы")
	is_running = False

# Регистрируем обработчики сигналов
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


@dp.message(Command("start"))
async def start(message: Message) -> None:
	await message.answer("Welcome! Use /switch_mode to search for a series.")


@dp.message(Command("help"))
async def help_command(message: Message) -> None:
	help_text = (
		"📖 <b>Доступные команды:</b>\n\n"
		"/start - Начать работу с ботом\n"
		"/help - Показать это сообщение\n"
		"/top_movies - Показать топ-10 самых популярных фильмов\n"
		"/search_by_description [описание] - Найти фильм по описанию\n"
		"/liked_movies - Показать список понравившихся фильмов\n"
		"/switch_mode - Переключить режим поиска (фильмы/сериалы)\n"
		"/history - Показать историю ваших запросов\n"
		"/popular_movies - Показать самые популярные запросы\n"
		"/menu - Показать главное меню с кнопками\n"
	)
	await message.answer(help_text, parse_mode="HTML")


@dp.message(Command("liked_movies"))
async def get_liked(message: Message) -> None:
	await message.answer("Fetching your liked movies...")
	user_id = message.chat.id
	liked_movies = stats.watch_liked_movies(user_id)
	if liked_movies:
		await message.answer("Your liked movies:\n" + "\n".join(liked_movies))
	else:
		await message.answer("You have no liked movies.")


@dp.message(Command("switch_mode"))
async def switch_mode(message: Message) -> None:
	chat_id = message.chat.id
	is_series_status[chat_id] = not is_series_status.get(chat_id, False)
	mode = "series" if is_series_status[chat_id] else "films"
	antimode = "films" if is_series_status[chat_id] else "series"
	await message.answer(
		f"Switched to {mode} mode. Use /switch_mode to search for a {antimode}."
	)


@dp.message(Command("history"))
async def show_history(message: Message) -> None:
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
async def top_movies(message: Message) -> None:
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
async def search_by_description(message: Message) -> None:
	if not message.text:
		await message.answer("Пожалуйста, укажите описание фильма после команды.")
		return
	args = message.text.split(maxsplit=1)[1:]
	description = args[0] if args else None
	if not description:
		await message.answer(
			"Пожалуйста, укажите описание фильма после команды."
		)
		return

	result = await search_movie_by_description(description)
	if result:
		await message.answer(f"🔍 Найденный фильм:\n\n{result}")
	else:
		await message.answer(
			"Не удалось найти фильм по описанию. Попробуйте позже."
		)


@dp.message(Command("popular_movies"))
async def popular_movies(message: Message) -> None:
	top_queries = stats.get_top_queries()
	if top_queries:
		response = "🎥 <b>Самые популярные запросы:</b>\n\n"
		for i, (query, count) in enumerate(top_queries, start=1):
			# Экранируем HTML-символы в запросе
			safe_query = query.replace("<", "&lt;").replace(">", "&gt;")
			response += f"{i}. <b>{safe_query}</b> — {count} раз(а)\n"
		await message.answer(response, parse_mode="HTML")
	else:
		await message.answer("Пока нет популярных запросов.")


@dp.message(Command("menu"))
async def menu(message: Message) -> None:
	keyboard = InlineKeyboardMarkup(
		inline_keyboard=[
			[InlineKeyboardButton(
				text="Популярные фильмы",
				callback_data="popular_movies"
			)]
		]
	)
	await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.callback_query(lambda callback: callback.data == "popular_movies")
async def show_popular_movies(callback_query: types.CallbackQuery) -> None:
	if not callback_query.message:
		return
	top_queries = stats.get_top_queries()
	if top_queries:
		response = "🎥 <b>Самые популярные запросы:</b>\n\n"
		for i, (query, count) in enumerate(top_queries, start=1):
			response += f"{i}. <b>{query}</b> — {count} раз(а)\n"
		await callback_query.message.edit_text(response, parse_mode="HTML")
	else:
		await callback_query.message.edit_text("Пока нет популярных запросов.")



async def show_film_card(
	chat_id: int,
	film_data: Dict[str, Any],
	is_series: bool = False
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
	
	title = film_data.get('title' if not is_series else 'name', 'N/A')
	release_date = film_data.get(
		'release_date' if not is_series else 'first_air_date',
		'N/A'
	)
	
	answer_text = (
		f"🎬 <b>{title}</b>\n\n"
		f"⭐ <b>Rating:</b> {film_data.get('vote_average', 'N/A')} {stars}\n"
		f"📅 <b>Date:</b> {release_date}\n"
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
		await bot.send_message(
			chat_id=chat_id,
			text=answer_text,
			parse_mode="HTML"
		)


@dp.message(lambda message: message.text in ["⏭", "❤️", "🎥"])
async def handle_movie_actions(message: Message) -> None:
	if message.text == "❤️":
		user_id = message.chat.id
		movie_title = "Unknown"
		if message.reply_to_message:
			if message.reply_to_message.caption:
				movie_title = message.reply_to_message.caption.split("\n")[0].replace("🎬 <b>", "").replace("</b>", "")
			elif message.reply_to_message.text:
				movie_title = message.reply_to_message.text.split("\n")[0].replace("🎬 <b>", "").replace("</b>", "")
		stats.save_liked_movie(user_id, movie_title)
		await message.answer("Фильм добавлен в избранное!")
	elif message.text == "🎥":
		await message.answer("В разработке")
	elif message.text == "⏭":
		await message.answer("В разработке")


@dp.message()
async def find_film(message: Message) -> None:
	if message.text:
		user_id = message.chat.id
		query = message.text
		stats.save_request(user_id, query)
		result = await search_movie(
			query,
			is_series=is_series_status.get(user_id, False)
		)
		if result and result.get("results"):
			await show_film_card(
				user_id,
				result["results"][0],
				is_series=is_series_status.get(user_id, False),
			)
		else:
			await message.answer(
				"Фильм не найден. Попробуйте другой запрос."
			)
	else:
		await message.answer("Пожалуйста, укажите название фильма.")


@dp.errors()
async def handle_errors(event: ErrorEvent) -> bool:
	logging.error(f"Ошибка: {event.exception}")
	return True


async def main() -> None:
	try:
		logger.info("Запуск бота...")
		await dp.start_polling(bot, skip_updates=True)
		
		# Ожидаем сигнала завершения
		while is_running:
			await asyncio.sleep(1)
			
	except Exception as e:
		logger.error(f"Ошибка при работе бота: {e}")
	finally:
		# Корректное завершение работы
		logger.info("Завершение работы бота...")
		await bot.session.close()
		stats.close_connection()
		logger.info("Бот остановлен")


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		logger.info("Бот остановлен пользователем")
	except Exception as e:
		logger.error(f"Критическая ошибка: {e}")
