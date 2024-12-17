from telebot.types import Message
from config import MESSAGES
from keyboards import get_main_keyboard

async def handle_music_link_message(bot, message: Message, get_user_lang, downloader):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    url = message.text.strip()
    
    if not any(domain in url.lower() for domain in ['youtube.com', 'youtu.be', 'spotify.com']):
        await bot.send_message(
            user_id, 
            MESSAGES[lang]['invalid_link'],
            reply_markup=get_main_keyboard(lang)
        )
        return
        
    await bot.send_message(
        user_id, 
        MESSAGES[lang]['downloading'],
        reply_markup=get_main_keyboard(lang)
    )
    
    try:
        if 'spotify.com' in url.lower():
            file_path, title = await downloader.process_spotify_link(url)
        else:
            file_path, title = await downloader.download_song(url)
            
        if file_path:
            with open(file_path, 'rb') as audio:
                await bot.send_audio(
                    user_id,
                    audio,
                    caption=f"🎵 {title}\n\n💫 Downloaded via @subralsb_musicbot",
                    title=title,
                    performer="subralsb",
                    reply_markup=get_main_keyboard(lang)
                )
        else:
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
