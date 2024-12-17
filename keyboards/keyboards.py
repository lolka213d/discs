from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import BUTTONS, SETTINGS_BUTTONS

def get_main_keyboard(lang):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton(BUTTONS[lang]['find_music']),
        KeyboardButton(BUTTONS[lang]['search_by_name']),
        KeyboardButton(BUTTONS[lang]['settings']),
        KeyboardButton(BUTTONS[lang]['donate'])
    ]
    keyboard.add(*buttons)
    return keyboard

def get_settings_keyboard(lang):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton(SETTINGS_BUTTONS[lang]['change_language']),
        KeyboardButton(SETTINGS_BUTTONS[lang]['help']),
        KeyboardButton(SETTINGS_BUTTONS[lang]['back'])
    ]
    keyboard.add(*buttons)
    return keyboard

def get_language_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        InlineKeyboardButton("Українська 🇺🇦", callback_data="lang_ua"),
        InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")
    )
    return keyboard

def get_donate_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💳 PrivatBank", url="https://www.privat24.ua/send/2cndq"),
        InlineKeyboardButton("🎁 Ko-fi", url="https://ko-fi.com/yevheniil")
    )
    return keyboard

def get_search_results_keyboard(results):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for result in results[:10]:
        button_text = f"🎵 {result['title']} ({result['duration']})"
        keyboard.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"yt_{result['id']}"
            )
        )
    return keyboard
