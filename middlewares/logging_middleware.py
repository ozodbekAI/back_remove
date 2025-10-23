# middleware/logging_middleware.py
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from utils.logger import logger

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, (Message, CallbackQuery)):
            logger.info(f"Event from {event.from_user.id if hasattr(event, 'from_user') else 'unknown'}: {getattr(event, 'text', getattr(event, 'data', 'no text'))}")
        return await handler(event, data)