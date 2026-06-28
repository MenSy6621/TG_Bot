from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from database.queries import (
    get_user_timezone,
    get_user_interval,
    set_user_interval
)


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    uid = message.from_user.id

    tz = await get_user_timezone(uid)

    interval = await get_user_interval(
        uid
    )

    # если пользователя ещё нет
    if interval is None:

        await set_user_interval(
            uid,
            30
        )

        interval = 30

    if tz is None:

        await message.answer(
            "Привет!\n\n"
            "Для работы напоминаний:\n\n"

            "1. Выберите часовой пояс\n"
            "/timezone\n\n"

            "2. Настройте интервал "
            "повторов для Done-уведомлений\n"

            "Команда:\n"
            "/interval 30\n\n"

            f"Текущий интервал: "
            f"{interval} мин"
        )

    else:

        await message.answer(
            "Привет!\n\n"

            f"🌍 Часовой пояс:\n"
            f"{tz}\n\n"

            f"⏱ Интервал повторов:\n"
            f"{interval} мин\n\n"

            "Изменить:\n"
            "/interval 30"
        )