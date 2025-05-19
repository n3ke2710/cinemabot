from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def construct_keyboard_markup() -> ReplyKeyboardMarkup:
	button_next = KeyboardButton(text="⏭", callback_data="next_next")
	button_watch = KeyboardButton(text="❤️", callback_data="movie_like")
	button_play = KeyboardButton(text="🎥", callback_data="movie_watch")

	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[button_watch, button_play, button_next]
		],
		resize_keyboard=True
	)
	return keyboard