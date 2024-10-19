from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Кнопки при старте
markup_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_talk = KeyboardButton("Talk with AI 🤖")
btn_find = KeyboardButton("Find apartments 🏘")
markup_start.row(btn_talk, btn_find)
markup_start.row(KeyboardButton('Help 🛟'), KeyboardButton("Description"))

# Кнопки для поиска
markup_find = ReplyKeyboardMarkup(one_time_keyboard=True)
btn_rent = KeyboardButton("Rent", callback_data="Rent")
btn_sale = KeyboardButton("Sale", callback_data="Sale")
markup_find.add(btn_rent, btn_sale)

# Кнопки для поиска для общения с AI
markup_talk = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn_audio = KeyboardButton("Audio", callback_data="handler_audio")
btn_text = KeyboardButton("Text", callback_data="handler_text")
markup_talk.row(btn_audio, btn_text)

# Кнопки для остановки бота
markup_stop = ReplyKeyboardMarkup(resize_keyboard=True)
btn_main_menu = KeyboardButton('Main menu')
markup_stop.add(btn_main_menu)
