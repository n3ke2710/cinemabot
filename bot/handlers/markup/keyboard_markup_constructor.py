from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def construct_keyboard_markup() -> InlineKeyboardMarkup:
	button_next = InlineKeyboardButton(text="⏭", callback_data="find_command_next_button")
	button_watch = InlineKeyboardButton(text="❤️", callback_data="like_command_film")
	button_play = InlineKeyboardButton(text="🎥", callback_data="find_command_watch_button")

	keyboard = InlineKeyboardMarkup(inline_keyboard=[[button_watch], [button_play], [button_next]])
	return keyboard