from telebot.types import Message
from config import MESSAGES
from keyboards import get_search_results_keyboard, get_main_keyboard

async def handle_text_message(bot, message: Message, get_user_lang, downloader, music_db):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    text = message.text.strip()

    if text.startswith(('http://', 'https://')):
        await handle_music_link_message(bot, message, get_user_lang, downloader, music_db)
        return

    await bot.send_message(
        user_id,
        MESSAGES[lang]['processing']
    )

    try:
        search_results = await downloader.search_songs(text)
        if search_results:
            await bot.send_message(
                user_id,
                "🎵 Found these songs:",
                reply_markup=get_search_results_keyboard(search_results)
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
            MESSAGES[lang]['download_error'],
            reply_markup=get_main_keyboard(lang)
        )
