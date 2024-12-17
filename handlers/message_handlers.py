from telebot.types import Message
from config import MESSAGES, BUTTONS, SETTINGS_BUTTONS
from keyboards import (
    get_main_keyboard,
    get_settings_keyboard,
    get_language_keyboard,
    get_donate_keyboard,
    get_search_results_keyboard
)

async def handle_text_message(bot, message: Message, get_user_lang, downloader, music_db):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    text = message.text

    # Main menu options
    if text == BUTTONS[lang]['find_music']:
        await bot.send_message(
            user_id,
            MESSAGES[lang]['send_audio'],
            reply_markup=get_main_keyboard(lang)
        )
        
    elif text == BUTTONS[lang]['search_by_name']:
        await bot.send_message(
            user_id,
            MESSAGES[lang]['enter_song_name'],
            reply_markup=get_main_keyboard(lang)
        )
        
    elif text == BUTTONS[lang]['settings']:
        await bot.send_message(
            user_id,
            MESSAGES[lang]['settings_menu'],
            reply_markup=get_settings_keyboard(lang)
        )
        
    elif text == BUTTONS[lang]['donate']:
        keyboard = get_donate_keyboard()
        await bot.send_message(
            user_id,
            MESSAGES[lang]['support_info'],
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    # Settings menu options
    elif text == SETTINGS_BUTTONS[lang]['change_language']:
        keyboard = get_language_keyboard()
        await bot.send_message(
            user_id,
            MESSAGES[lang]['choose_language'],
            reply_markup=keyboard
        )
        
    elif text == SETTINGS_BUTTONS[lang]['help']:
        await bot.send_message(
            user_id,
            MESSAGES[lang]['help'],
            reply_markup=get_settings_keyboard(lang)
        )
        
    elif text == SETTINGS_BUTTONS[lang]['back']:
        await bot.send_message(
            user_id,
            MESSAGES[lang]['main_menu'],
            reply_markup=get_main_keyboard(lang)
        )

    # Handle music search
    elif text and not text.startswith('/'):
        try:
            await bot.send_message(
                user_id,
                MESSAGES[lang]['searching'],
                reply_markup=get_main_keyboard(lang)
            )
            
            results = await downloader.search_songs(text)
            
            if results:
                keyboard = get_search_results_keyboard(results)
                await bot.send_message(
                    user_id,
                    MESSAGES[lang]['choose_version'],
                    reply_markup=keyboard
                )
            else:
                await bot.send_message(
                    user_id,
                    MESSAGES[lang]['no_results'],
                    reply_markup=get_main_keyboard(lang)
                )
                
        except Exception as e:
            print(f"Search error: {e}")
            await bot.send_message(
                user_id,
                MESSAGES[lang]['search_error'],
                reply_markup=get_main_keyboard(lang)
            )
