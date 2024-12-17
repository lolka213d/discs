from telebot.types import CallbackQuery
import os
from config import MESSAGES
from keyboards import (
    get_main_keyboard,
    get_settings_keyboard,
    get_language_keyboard,
    get_donate_keyboard,
    get_search_results_keyboard
)

async def handle_callback(bot, call: CallbackQuery, get_user_lang, downloader, music_db):
    user_id = call.from_user.id
    lang = get_user_lang(user_id)
    
    if call.data.startswith(('yt_', 'sp_')):
        source_type, track_id = call.data.split('_')
        await bot.edit_message_text(
            MESSAGES[lang]['downloading'],
            user_id,
            call.message.message_id
        )
        
        try:
            result = None
            if source_type == 'yt':
                result = await downloader.download_song(f"https://youtube.com/watch?v={track_id}")
            else:
                result = await downloader.process_spotify_link(f"https://open.spotify.com/track/{track_id}")
                
            if result and isinstance(result, tuple) and len(result) == 2:
                file_path, title = result
                if file_path and os.path.exists(file_path):
                    with open(file_path, 'rb') as audio:
                        await bot.send_audio(
                            user_id,
                            audio,
                            caption=f"🎵 {title}\n\n💫 Downloaded via @subralsb_musicbot",
                            title=title,
                            performer="subralsb",
                            reply_markup=get_main_keyboard(lang)
                        )
                    await music_db.add_song(title, None, track_id, source_type, file_path)
                    os.remove(file_path)
                    return
                    
            await bot.send_message(
                user_id,
                MESSAGES[lang]['download_error'],
                reply_markup=get_main_keyboard(lang)
            )
        except Exception as e:
            print(f"Download error: {e}")
            await bot.send_message(
                user_id,
                MESSAGES[lang]['download_error'],
                reply_markup=get_main_keyboard(lang)
            )
    
    elif call.data == 'settings':
        await bot.edit_message_text(
            MESSAGES[lang]['settings_menu'],
            user_id,
            call.message.message_id,
            reply_markup=get_settings_keyboard(lang)
        )
    
    elif call.data == 'change_language':
        await bot.edit_message_text(
            MESSAGES[lang]['choose_language'],
            user_id,
            call.message.message_id,
            reply_markup=get_language_keyboard()
        )
    
    elif call.data.startswith('lang_'):
        new_lang = call.data.split('_')[1]
        bot.user_languages[user_id] = new_lang
        await bot.edit_message_text(
            MESSAGES[new_lang]['language_changed'],
            user_id,
            call.message.message_id,
            reply_markup=get_main_keyboard(new_lang)
        )
    
    elif call.data == 'support':
        await bot.edit_message_text(
            MESSAGES[lang]['support_info'],
            user_id,
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=get_donate_keyboard()
        )
    
    elif call.data == 'back_to_menu':
        await bot.edit_message_text(
            MESSAGES[lang]['welcome_text'],
            user_id,
            call.message.message_id,
            reply_markup=get_main_keyboard(lang)
        )
    
    elif call.data == 'help':
        await bot.edit_message_text(
            MESSAGES[lang]['help'],
            user_id,
            call.message.message_id,
            reply_markup=get_settings_keyboard(lang)
        )
        
    await bot.answer_callback_query(call.id)
