import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.queries import (
    set_user_interval,
    get_user_interval
)

router = Router()

logger = logging.getLogger(__name__)


@router.message(Command("interval"))
async def interval_handler(
    message: Message
):

    try:

        args = message.text.replace(
            "/interval",
            "",
            1
        ).strip()

        # показать текущий
        if not args:

            interval = await get_user_interval(
                message.from_user.id
            )

            await message.answer(
                f"⏱ Текущий интервал:\n"
                f"{interval} мин\n\n"
                f"Изменить:\n"
                f"/interval 30"
            )

            return

        try:

            minutes = int(args)

        except ValueError:

            await message.answer(
                "❌ Интервал должен быть числом\n\n"
                "Пример:\n"
                "/interval 30"
            )

            return

        if minutes < 1:

            await message.answer(
                "❌ Минимум 1 минута"
            )

            return

        await set_user_interval(
            message.from_user.id,
            minutes
        )

        logger.info(
            f"User {message.from_user.id} "
            f"set interval {minutes}"
        )

        await message.answer(
            f"✅ Интервал повторов "
            f"установлен:\n"
            f"{minutes} мин"
        )

    except Exception as e:

        logger.exception(e)

        await message.answer(
            "❌ Ошибка"
        )