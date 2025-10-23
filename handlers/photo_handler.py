import asyncio
import uuid
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from services.image_service import ImageService
from keyboards.inline_keyboards import get_result_keyboard
from utils.file_utils import download_temp_file, save_temp_bytes, cleanup_file, cleanup_temp_dir
from photos.processor import validate_image_bytes, is_valid_image_file
from config import settings
from utils.logger import logger

router = Router()

async def process_image_with_retry(original_bytes, retries=2):
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            clean_bytes = ImageService.remove_background(original_bytes)
            watermarked_bytes = ImageService.add_watermarks(clean_bytes)
            return clean_bytes, watermarked_bytes
        except Exception as e:
            last_exception = e
            await asyncio.sleep(1)  
    raise last_exception


@router.message(F.photo)
async def photo_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if message.caption:
        return

    temp_path = temp_dir = water_path = None
    try:
        await message.answer("⏳ Обрабатываю изображение... Это может занять до 1 минуты.")

        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        temp_path, temp_dir = await download_temp_file(message.bot, file.file_path, user_id)

        with open(temp_path, "rb") as f:
            original_bytes = f.read()

        if not validate_image_bytes(original_bytes):
            await message.answer("❌ Неверный формат фото. Попробуйте JPEG или PNG.")
            return

        clean_bytes, watermarked_bytes = await process_image_with_retry(original_bytes, retries=2)

        image_key = str(uuid.uuid4())
        logger.info(f"User {user_id}: Generated key {image_key} for document, clean_bytes size: {len(clean_bytes)}")

        water_path = await save_temp_bytes(watermarked_bytes, f"water_{user_id}_{image_key}.png")
        markup = get_result_keyboard(user_id, image_key)

        result_msg = await message.answer_photo(
            photo=FSInputFile(water_path),
            caption=(
                "✅ Готово — пример с водяными знаками.\n\n"
                f"💰 Полная версия без водяных знаков — {settings.price}₽\n"
                "Нажмите кнопку ниже, чтобы оплатить."
            ),
            reply_markup=markup,
            reply_to_message_id=message.message_id
        )

        data = await state.get_data()
        images = data.get('images', {})
        images[image_key] = {
            'clean': clean_bytes,
            'watermarked': watermarked_bytes,
            'paid': False,
            'result_msg_id': result_msg.message_id
        }
        await state.update_data(images=images)
        logger.info(f"Added document {image_key} to state for user {user_id}, current keys: {list(images.keys())}")

    except Exception as e:
        logger.exception(f"Error in photo_handler for user {user_id}: {e}")
        await message.answer("❌ Ошибка при обработке фото. Попробуйте другую фотографию.")
    finally:
        cleanup_file(temp_path)
        cleanup_file(water_path)
        if temp_dir:
            cleanup_temp_dir(temp_dir)

@router.message(F.document)
async def document_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if message.caption:
        return

    temp_path = temp_dir = water_path = None
    try:
        await message.answer("⏳ Обрабатываю файл... Это может занять до 1 минуты.")

        document = message.document 
        if not is_valid_image_file(document.file_name, document.mime_type):
            await message.answer("❌ Файл не является изображением.")
            return

        file = await message.bot.get_file(document.file_id)
        temp_path, temp_dir = await download_temp_file(message.bot, file.file_path, user_id)

        with open(temp_path, "rb") as f:
            original_bytes = f.read()

        if not validate_image_bytes(original_bytes):
            await message.answer("❌ Неверный формат файла. Попробуйте JPEG или PNG.")
            return

        clean_bytes, watermarked_bytes = await process_image_with_retry(original_bytes, retries=2)

        # UNIQUE KEY
        image_key = str(uuid.uuid4())
        logger.info(f"User {user_id}: Generated key {image_key} for document, clean_bytes size: {len(clean_bytes)}")

        water_path = await save_temp_bytes(watermarked_bytes, f"water_{user_id}_{image_key}.png")
        markup = get_result_keyboard(user_id, image_key)

        result_msg = await message.answer_document(
            document=FSInputFile(water_path, filename="background_removed_watermark.png"),
            caption=(
                "✅ Превью с водяными знаками.\n\n"
                f"💰 Для получения версии без водяных знаков — оплатите {settings.price}₽"
            ),
            reply_markup=markup,
            reply_to_message_id=message.message_id
        )

        data = await state.get_data()
        images = data.get('images', {})
        images[image_key] = {
            'clean': clean_bytes,
            'watermarked': watermarked_bytes,
            'paid': False,
            'result_msg_id': result_msg.message_id
        }
        await state.update_data(images=images)
        logger.info(f"Added document {image_key} to state for user {user_id}, current keys: {list(images.keys())}")

    except Exception as e:
        await message.answer("❌ Ошибка при обработке файла. Попробуйте снова.")
    finally:
        cleanup_file(temp_path)
        cleanup_file(water_path)
        if temp_dir:
            cleanup_temp_dir(temp_dir)