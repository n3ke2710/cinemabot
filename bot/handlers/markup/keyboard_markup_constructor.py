from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def construct_keyboard_markup() -> ReplyKeyboardMarkup:
	# button_next = KeyboardButton(text="⏭")
	button_like = KeyboardButton(text="❤️")
	# button_play = KeyboardButton(text="🎥")

	keyboard = ReplyKeyboardMarkup(
		keyboard=[
			[button_like]
		],
		resize_keyboard=True
	)
	return keyboard