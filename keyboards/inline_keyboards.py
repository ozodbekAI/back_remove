from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_result_keyboard(user_id: int, image_index: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"pay_{user_id}_{image_index}")],
        [InlineKeyboardButton(text="Не нравится результат", callback_data="not_like")]
    ])

def get_payment_keyboard(invoice_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить в ЮKassa", url=invoice_url)]
    ])

def get_paid_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оплата прошла", callback_data="paid_done")],
        [InlineKeyboardButton(text="Не нравится результат", callback_data="not_like")]
    ])