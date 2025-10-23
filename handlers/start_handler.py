# handlers/start_handler.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_async_session
from repositories.user_repository import UserRepository
from utils.logger import logger

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    async for session in get_async_session():
        user_repo = UserRepository(session)
        await user_repo.get_or_create(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name
        )
    await message.answer(
        "Привет! Я бот для удаления фона на фотографиях. "
        "Загрузите фото, и я обработаю его бесплатно (с водяными знаками). "
        "Если понравится, оплатите полную версию без водяных знаков!"
    )