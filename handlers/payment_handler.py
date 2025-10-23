from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from services.payment_service import PaymentService
from services.image_service import ImageService
from keyboards.inline_keyboards import get_payment_keyboard, get_paid_keyboard, get_result_keyboard
from utils.file_utils import save_temp_bytes, cleanup_file
from database.connection import get_async_session
from config import settings
from utils.logger import logger
import asyncio

router = Router()


@router.callback_query(F.data.startswith("pay_"))
async def payment_handler(callback: CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split("_", 2) 
        if len(parts) < 3:
            await callback.answer("❌ Неверный формат запроса!", show_alert=True)
            return
        user_id = int(parts[1])
        image_key = parts[2]  # Endi key str

        data = await state.get_data()
        images = data.get("images", {})
        if image_key not in images or images[image_key].get('paid'):
            await callback.answer("❌ Изображение не найдено или уже оплачено! Сначала отправьте фотографию.", show_alert=True)
            return

        logger.info(f"Payment button clicked: user {user_id}, key {image_key}, images keys: {list(images.keys())}")

        processing_markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏳ Оплата в процессе...", callback_data=f"pay_processing_{user_id}_{image_key}")],
            [InlineKeyboardButton(text="Не нравится результат", callback_data="not_like")]
        ])
        await callback.message.edit_reply_markup(reply_markup=processing_markup)

        await state.update_data(selected_image_key=image_key)

        async for session in get_async_session():
            invoice_url, invoice_id = await PaymentService.create_invoice(session, user_id)

        markup = get_payment_keyboard(invoice_url)
        msg = await callback.message.answer("💳 Перейдите по ссылке для оплаты:", reply_markup=markup)
        await callback.answer()

        asyncio.create_task(
            poll_for_payment(
                telegram_id=user_id,
                invoice_id=invoice_id,
                state=state,
                bot=callback.bot,
                payment_message_id=msg.message_id,
                image_key=image_key 
            )
        )

    except Exception as e:
        logger.error(f"Payment handler error: {e}")
        await callback.answer("Ошибка создания платежа. Попробуйте позже.", show_alert=True)
        markup = get_result_keyboard(user_id, image_key)
        await callback.message.edit_reply_markup(reply_markup=markup)


async def poll_for_payment(telegram_id: int, invoice_id: str, state: FSMContext, bot, payment_message_id: int, image_key: str):  # Key str

    while True:
        await asyncio.sleep(10) 
        async for session in get_async_session():
            if await PaymentService.check_status(session, invoice_id):
                try:
                    await bot.edit_message_text(
                        chat_id=telegram_id,
                        message_id=payment_message_id,
                        text="✅ Оплата успешно получена! Отправляю фотографию без водяных знаков..."
                    )
                except:
                    pass

                data = await state.get_data()
                images = data.get("images", {})
                logger.info(f"Poll start for user {telegram_id}, requested key {image_key}, images keys: {list(images.keys())}")

                if image_key in images:
                    img_data = images[image_key]
                    clean_bytes = img_data['clean']
                    result_msg_id = img_data['result_msg_id']
                    logger.info(f"Sending clean for key {image_key}: bytes size {len(clean_bytes)}, msg_id {result_msg_id}")

                    temp_path = await save_temp_bytes(clean_bytes, f"clean_{telegram_id}_{image_key}.png")
                    await bot.send_document(
                        telegram_id,
                        document=FSInputFile(temp_path, filename="photo_clean.png"),
                        caption="✅ Спасибо за оплату! Вот ваша фотография без водяных знаков 🙌"
                    )
                    cleanup_file(temp_path)

                    if result_msg_id:
                        try:
                            await bot.edit_message_reply_markup(
                                chat_id=telegram_id,
                                message_id=result_msg_id,
                                reply_markup=get_paid_keyboard()
                            )
                        except Exception as e:
                            logger.error(f"Failed to edit result message {result_msg_id}: {e}")

                    images[image_key]['paid'] = True
                    await state.update_data(images=images)
                    logger.info(f"Payment completed for key {image_key}, updated paid=True")

                await asyncio.sleep(2)
                await bot.send_message(
                    telegram_id,
                    "📸 Хотите обработать ещё одну фотографию?\n"
                    "Просто отправьте её в чат 👇\n\n"
                    f"💰 Стоимость обработки: {settings.price}₽"
                )
                return

@router.callback_query(F.data == "not_like")
async def not_like_handler(callback: CallbackQuery):
    await callback.message.answer(
        f"📩 Отправьте фотографию в поддержку {settings.support_username} и опишите проблему. Мы поможем!"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay_processing_"))
async def pay_processing_handler(callback: CallbackQuery):
    await callback.answer("⏳ Оплата в процессе. Пожалуйста, подождите подтверждения.", show_alert=True)


@router.callback_query(F.data == "paid_done")
async def paid_done_handler(callback: CallbackQuery):
    await callback.answer("✅ Изображение уже отправлено! Хотите обработать ещё одну фотографию?", show_alert=True)