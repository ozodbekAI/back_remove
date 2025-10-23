# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import settings
from handlers import start_router, photo_router, payment_router, admin_router
from middlewares.logging_middleware import LoggingMiddleware
from database.connection import init_db
from utils.logger import logger

async def main():
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.outer_middleware(LoggingMiddleware())
    dp.callback_query.outer_middleware(LoggingMiddleware())

    dp.include_router(start_router)
    dp.include_router(photo_router)
    dp.include_router(payment_router)
    dp.include_router(admin_router)

    logger.info("Starting bot polling...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")