from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database.connection import get_async_session
from repositories.user_repository import UserRepository
from config import settings
from utils.logger import logger

router = Router()

@router.message(Command("admin"))
async def admin_handler(message: Message):
    if message.from_user.id not in settings.admin_ids:
        await message.answer("Доступ запрещен.")
        return

    async for session in get_async_session():
        user_repo = UserRepository(session)
        stats = await user_repo.get_stats()

    stats_text = f"""
📊 Статистика бота:

• Новых пользователей сегодня: {stats['new_today']}
• Новых пользователей вчера: {stats['new_yesterday']}
• Всего пользователей: {stats['total']}
    """
    await message.answer(stats_text)
    logger.info(f"Admin stats requested by {message.from_user.id}")