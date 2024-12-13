import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.telegrambot.config import TOKEN
from app.telegrambot.handlers import router

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    dp = Dispatcher()
    dp.include_router(router)
    
    try:
        bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        logging.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Bot stopped by user')
