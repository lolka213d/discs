import os
import asyncio
from shazamio import Shazam
from telebot.types import Message
from config import MESSAGES
from keyboards import get_main_keyboard

async def download_voice(bot, file_id, file_path):
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

async def recognize_song(audio_file):
    shazam = Shazam()
    try:
        recognition_result = await shazam.recognize_song(audio_file)
        if recognition_result and recognition_result.get('track'):
            track = recognition_result['track']
            return {
                'title': track.get('title', 'Unknown'),
                'artist': track.get('subtitle', 'Unknown Artist'),
                'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown Album'),
                'url': track.get('share', {}).get('href', ''),
                'spotify_url': next((provider['actions'][0]['uri'] 
                    for provider in track.get('hub', {}).get('providers', [])
                    if provider['type'] == 'SPOTIFY'), ''),
                'youtube_url': next((provider['actions'][0]['uri']
                    for provider in track.get('hub', {}).get('providers', [])
                    if provider['type'] == 'YOUTUBE'), '')
            }
        return None
    except Exception as e:
        print(f"Shazam recognition error: {e}")
        return None

async def handle_audio_message(bot, message: Message, get_user_lang):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    if not message.audio and not message.voice:
        await bot.send_message(
            user_id, 
            MESSAGES[lang]['send_audio'],
            reply_markup=get_main_keyboard(lang)
        )
        return
        
    await bot.send_message(
        user_id, 
        MESSAGES[lang]['processing'],
        reply_markup=get_main_keyboard(lang)
    )
    
    try:
        file_id = message.audio.file_id if message.audio else message.voice.file_id
        temp_file = f"temp_audio_{user_id}.ogg"
        
        await download_voice(bot, file_id, temp_file)
        shazam_results = await recognize_song(temp_file)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        if shazam_results:
            song_info = (
                f"🎵 Found: {shazam_results['title']}\n"
                f"👤 Artist: {shazam_results['artist']}\n"
                f"💿 Album: {shazam_results['album']}\n\n"
                f"🔗 Links:\n"
                f"🎧 Shazam: {shazam_results['url']}\n"
                f"📀 Spotify: {shazam_results['spotify_url']}\n"
                f"▶️ YouTube: {shazam_results['youtube_url']}"
            )
            
            await bot.send_message(
                user_id,
                song_info,
                parse_mode='HTML',
                reply_markup=get_main_keyboard(lang)
            )
        else:
            await bot.send_message(
                user_id,
                MESSAGES[lang]['no_results'],
                reply_markup=get_main_keyboard(lang)
            )
            
    except Exception as e:
        print(f"Audio processing error: {e}")
        await bot.send_message(
            user_id,
            MESSAGES[lang]['recognition_error'],
            reply_markup=get_main_keyboard(lang)
        )
