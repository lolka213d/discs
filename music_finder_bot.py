from telebot.async_telebot import AsyncTeleBot
import asyncio
import logging
import os
from time import sleep
from config.settings import TOKEN
from handlers import (
    setup_commands,
    handle_audio_message,
    handle_music_link_message,
    handle_callback,
    handle_text_message
)
from database import MusicDatabase
from utils import MusicDownloader, clean_old_files
from keyboards import (
    get_main_keyboard,
    get_settings_keyboard,
    get_language_keyboard,
    get_search_results_keyboard
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot.log'
)
logger = logging.getLogger(__name__)

class MusicBot:
    def __init__(self):
        self.bot = AsyncTeleBot(TOKEN)
        self.downloads_dir = "downloads"
        os.makedirs(self.downloads_dir, exist_ok=True)
        
        logger.info("🚀 Initializing bot...")
        self.music_db = MusicDatabase()
        logger.info("✅ Database connected successfully")
        
        self.downloader = MusicDownloader(self.downloads_dir)
        self.user_languages = {}
        self.active_downloads = set()
        self.user_states = {}

    def get_user_lang(self, user_id):
        return self.user_languages.get(user_id, 'en')

    async def setup_handlers(self):
        # Инициализируем обработчики из commands.py
        handle_commands, handle_all_messages, callback_handler, handle_donate = setup_commands(
            self.bot,
            self.get_user_lang,
            handle_audio_message,
            handle_music_link_message,
            self.music_db,
            self.downloader,
            self.downloads_dir
        )
        
        # Регистрируем обработчики
        self.bot.message_handler(commands=['start', 'help', 'download', 'language', 'donate'])(handle_commands)
        self.bot.message_handler(func=lambda message: True)(handle_all_messages)
        self.bot.callback_query_handler(func=lambda call: True)(callback_handler)

        @self.bot.message_handler(content_types=['audio', 'voice'])
        async def audio_handler(message):
            try:
                await handle_audio_message(self.bot, message, self.get_user_lang)
            except Exception as e:
                logger.error(f"Audio handler error: {e}")
                await self.handle_error(message.chat.id)

        @self.bot.message_handler(content_types=['text'])
        async def text_handler(message):
            try:
                if message.text.startswith(('http://', 'https://')):
                    await handle_music_link_message(
                        self.bot, message, self.get_user_lang,
                        self.downloader, self.music_db
                    )
                else:
                    await handle_text_message(
                        self.bot, message, self.get_user_lang,
                        self.downloader, self.music_db
                    )
            except Exception as e:
                logger.error(f"Text handler error: {e}")
                await self.handle_error(message.chat.id)

    async def handle_error(self, chat_id):
        lang = self.get_user_lang(chat_id)
        try:
            await self.bot.send_message(
                chat_id,
                "An error occurred. Please try again.",
                reply_markup=get_main_keyboard(lang)
            )
        except Exception as e:
            logger.error(f"Error handler failed: {e}")

    async def clean_downloads_task(self):
        while True:
            try:
                clean_old_files(self.downloads_dir)
                await asyncio.sleep(3600)
            except Exception as e:
                logger.error(f"Clean downloads error: {e}")
                await asyncio.sleep(60)

    async def run(self):
        logger.info("🎵 Bot started successfully!")
        try:
            asyncio.create_task(self.clean_downloads_task())
            await self.bot.polling(non_stop=True, timeout=60)
        except Exception as e:
            logger.error(f"Polling error: {e}")
            await asyncio.sleep(5)
            await self.run()

async def main():
    try:
        logger.info("🎵 Starting Music Bot...")
        bot = MusicBot()
        logger.info("⚙️ Setting up handlers...")
        await bot.setup_handlers()
        logger.info("✨ Bot is ready! Starting polling...")
        await bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        await bot.bot.close_session()
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("👋 Goodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down gracefully...")
