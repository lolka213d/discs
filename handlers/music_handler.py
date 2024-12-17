from telebot import types
from config import MESSAGES, BUTTONS

async def handle_music_search(bot, message, get_user_lang, downloader, music_db):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    if message.text == BUTTONS[lang]['cancel']:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(
            types.KeyboardButton(BUTTONS[lang]['find_music']),
            types.KeyboardButton(BUTTONS[lang]['search_by_name']),
            types.KeyboardButton(BUTTONS[lang]['settings']),
            types.KeyboardButton(BUTTONS[lang]['donate'])
        )
        await bot.send_message(user_id, MESSAGES[lang]['operation_cancelled'], reply_markup=keyboard)
        return

    await process_song_search(bot, message, get_user_lang, downloader, music_db)

async def process_song_search(bot, message, get_user_lang, downloader, music_db):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    query = message.text.strip()

    if not query:
        await bot.send_message(user_id, MESSAGES[lang]['enter_song_name'])
        return

    try:
        await bot.send_message(user_id, MESSAGES[lang]['searching'])
        results = downloader.get_search_results(query)
        
        if not results:
            await bot.send_message(user_id, MESSAGES[lang]['no_results'])
            return

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for result in results[:10]:  # Show first 10 results
            button_text = f"🎵 {result['title']} ({result['duration']})"
            callback_data = result['callback_data']  # Используем callback_data вместо id
            keyboard.add(
                types.InlineKeyboardButton(
                    text=button_text,
                    callback_data=callback_data
                )
            )

        await bot.send_message(
            user_id,
            MESSAGES[lang]['choose_version'],
            reply_markup=keyboard
        )

    except Exception as e:
        print(f"Search error: {e}")
        await bot.send_message(user_id, MESSAGES[lang]['search_error'])
