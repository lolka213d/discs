import os
import threading
import asyncio
from telebot import types
from config import MESSAGES, BUTTONS, SETTINGS_BUTTONS
from handlers.audio_handler import handle_audio_message
from handlers.music_handler import handle_music_search, process_song_search
from handlers.callback_handler import handle_callback

def setup_commands(bot, get_user_lang, handle_audio, handle_music_link, music_db, downloader, downloads_dir):
    user_data = {}
    user_languages = {}

    def create_keyboard_buttons(lang):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [
            types.KeyboardButton(BUTTONS[lang]['find_music']),
            types.KeyboardButton(BUTTONS[lang]['search_by_name']),
            types.KeyboardButton(BUTTONS[lang]['settings']),
            types.KeyboardButton(BUTTONS[lang]['donate'])
        ]
        keyboard.add(*buttons)
        return keyboard

    def create_settings_keyboard(lang):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [
            types.KeyboardButton(SETTINGS_BUTTONS[lang]['change_language']),
            types.KeyboardButton(SETTINGS_BUTTONS[lang]['help']),
            types.KeyboardButton(SETTINGS_BUTTONS[lang]['back'])
        ]
        keyboard.add(*buttons)
        return keyboard

    def create_language_keyboard():
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
            types.InlineKeyboardButton("Українська 🇺🇦", callback_data="lang_ua"),
            types.InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru")
        )
        return keyboard

    async def handle_donate(message):
        user_id = message.from_user.id
        lang = get_user_lang(user_id)
        
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("💳 PrivatBank", url="https://www.privat24.ua/send/2cndq"),
            types.InlineKeyboardButton("🎁 Ko-fi", url="https://ko-fi.com/yevheniil")
        )
        
        await bot.send_message(
            user_id, 
            MESSAGES[lang]['support_info'], 
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    async def handle_audio_wrapper(message):
        await handle_audio_message(bot, message, get_user_lang)

    async def handle_music_search_wrapper(message):
        await handle_music_search(bot, message, get_user_lang, downloader, music_db)

    @bot.message_handler(commands=['start', 'help', 'download', 'language', 'donate'])
    async def handle_commands(message):
        command = message.text[1:]
        user_id = message.from_user.id
        lang = get_user_lang(user_id)
        
        if command == 'start':
            keyboard = create_keyboard_buttons(lang)
            welcome_text = MESSAGES[lang]['welcome_text']
            await bot.reply_to(message, welcome_text, reply_markup=keyboard)
            await bot.send_message(user_id, MESSAGES[lang]['spotify_info'])
        elif command == 'help':
            await bot.reply_to(message, MESSAGES[lang]['help'])
        elif command == 'download':
            await bot.reply_to(message, MESSAGES[lang]['send_link'])
        elif command == 'language':
            keyboard = create_language_keyboard()
            await bot.reply_to(message, MESSAGES[lang]['choose_language'], reply_markup=keyboard)
        elif command == 'donate':
            await handle_donate(message)

    @bot.message_handler(func=lambda message: message.text in [BUTTONS['en']['settings'], BUTTONS['ua']['settings'], BUTTONS['ru']['settings']])
    async def handle_settings(message):
        user_id = message.from_user.id
        lang = get_user_lang(user_id)
        keyboard = create_settings_keyboard(lang)
        await bot.send_message(user_id, MESSAGES[lang]['settings_menu'], reply_markup=keyboard)

    @bot.message_handler(func=lambda message: message.text in [SETTINGS_BUTTONS['en']['back'], SETTINGS_BUTTONS['ua']['back'], SETTINGS_BUTTONS['ru']['back']])
    async def handle_back_to_menu(message):
        user_id = message.from_user.id
        lang = get_user_lang(user_id)
        keyboard = create_keyboard_buttons(lang)
        await bot.send_message(user_id, MESSAGES[lang]['main_menu'], reply_markup=keyboard)

    @bot.message_handler(content_types=['text'])
    async def handle_all_messages(message):
        user_id = message.from_user.id
        lang = get_user_lang(user_id)
        text = message.text

        if text == BUTTONS[lang]['search_by_name']:
            await bot.send_message(user_id, MESSAGES[lang]['enter_song_name'])
            user_data[user_id] = {'state': 'waiting_for_song_name'}
            
        elif text == BUTTONS[lang]['find_music']:
            await bot.send_message(user_id, MESSAGES[lang]['send_audio'])
            user_data[user_id] = {'state': 'waiting_for_audio'}
            
        elif text == SETTINGS_BUTTONS[lang]['change_language']:
            keyboard = create_language_keyboard()
            await bot.send_message(user_id, MESSAGES[lang]['choose_language'], reply_markup=keyboard)
            
        elif text == SETTINGS_BUTTONS[lang]['help']:
            await bot.send_message(user_id, MESSAGES[lang]['help'])
            
        elif text in [BUTTONS['en']['donate'], BUTTONS['ua']['donate'], BUTTONS['ru']['donate']]:
            await handle_donate(message)
            
        elif user_id in user_data:
            state = user_data[user_id].get('state')
            if state == 'waiting_for_song_name':
                await handle_music_search_wrapper(message)
                del user_data[user_id]
            elif state == 'waiting_for_audio':
                await handle_audio_wrapper(message)
                del user_data[user_id]

    @bot.callback_query_handler(func=lambda call: True)
    async def callback_handler(call):
        user_id = call.from_user.id
        lang = get_user_lang(user_id)
        
        try:
            if call.data.startswith('lang_'):
                new_lang = call.data.split('_')[1]
                user_languages[user_id] = new_lang
                keyboard = create_keyboard_buttons(new_lang)
                await bot.send_message(user_id, MESSAGES[new_lang]['language_changed'], reply_markup=keyboard)
            else:
                await handle_callback(bot, call, get_user_lang, downloader, music_db)
                
        except Exception as e:
            print(f"Callback error: {e}")
            await bot.send_message(user_id, MESSAGES[lang]['download_error'])

    return handle_commands, handle_all_messages, callback_handler, handle_donate
