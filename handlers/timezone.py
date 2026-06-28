from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import TIMEZONE_GROUPS
from database.queries import set_user_timezone


router = Router()


def get_countries_keyboard():

    buttons = []

    countries = list(TIMEZONE_GROUPS.keys())

    for index, country in enumerate(countries):

        buttons.append([
            InlineKeyboardButton(
                text=country,
                callback_data=f"tz_country:{index}"
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


def get_cities_keyboard(country_index: int):

    countries = list(TIMEZONE_GROUPS.keys())

    country_name = countries[country_index]

    cities = TIMEZONE_GROUPS[country_name]

    buttons = []

    for city_name, tz_name in cities:

        buttons.append([
            InlineKeyboardButton(
                text=city_name,
                callback_data=f"tz_set:{tz_name}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="tz_back"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


@router.message(F.text == "/timezone")
async def timezone_command(message: Message):

    await message.answer(
        "Выберите регион:",
        reply_markup=get_countries_keyboard()
    )


@router.callback_query(F.data == "tz_back")
async def timezone_back(callback: CallbackQuery):

    await callback.message.edit_text(
        "Выберите регион:",
        reply_markup=get_countries_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("tz_country:"))
async def timezone_country(callback: CallbackQuery):

    country_index = int(
        callback.data.split(":")[1]
    )

    countries = list(TIMEZONE_GROUPS.keys())

    country_name = countries[country_index]

    await callback.message.edit_text(
        f"Выберите город\n\n{country_name}",
        reply_markup=get_cities_keyboard(country_index)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("tz_set:"))
async def timezone_set(callback: CallbackQuery):

    tz_name = callback.data.split(":")[1]

    await set_user_timezone(
        callback.from_user.id,
        tz_name
    )

    await callback.message.edit_text(
        f"✅ Часовой пояс установлен\n\n{tz_name}"
    )

    await callback.answer()