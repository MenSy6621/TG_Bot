import logging

from aiogram import Bot

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import BOT_TOKEN

logger = logging.getLogger(__name__)


async def send_reminder(
    user_id,
    text,
    task_id
):
    try:
        bot = Bot(BOT_TOKEN)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Done",
                callback_data=f"done:{task_id}"
            ),
            InlineKeyboardButton(
                text="⏳ Delay",
                callback_data=f"delay:{task_id}"
            )
        ]
    ]
        )

        await bot.send_message(
            chat_id=user_id,
            text=f"⏰ {text}",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.exception(e)