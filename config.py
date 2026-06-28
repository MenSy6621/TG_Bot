import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_PATH = "tasks.db"

LOG_LEVEL = "INFO"

TIMEZONE_GROUPS = {
    "🇷🇺 Россия": [
        ("Москва (UTC+3)", "Europe/Moscow"),
        ("Калининград (UTC+2)", "Europe/Kaliningrad"),
        ("Самара (UTC+4)", "Europe/Samara"),
        ("Екатеринбург (UTC+5)", "Asia/Yekaterinburg"),
        ("Омск (UTC+6)", "Asia/Omsk"),
        ("Томск (UTC+7)", "Asia/Tomsk"),
        ("Красноярск (UTC+7)", "Asia/Krasnoyarsk"),
        ("Иркутск (UTC+8)", "Asia/Irkutsk"),
        ("Якутск (UTC+9)", "Asia/Yakutsk"),
        ("Владивосток (UTC+10)", "Asia/Vladivostok"),
        ("Магадан (UTC+11)", "Asia/Magadan"),
        ("Камчатка (UTC+12)", "Asia/Kamchatka"),
    ],

    "🇰🇿 Казахстан": [
        ("Алматы (UTC+5)", "Asia/Almaty"),
        ("Астана (UTC+5)", "Asia/Almaty"),
    ],

    "🇪🇺 Европа": [
        ("Рига (UTC+3)", "Europe/Riga"),
        ("Берлин (UTC+2)", "Europe/Berlin"),
        ("Лондон (UTC+1)", "Europe/London"),
        ("Париж (UTC+2)", "Europe/Paris"),
    ],

    "🇺🇸 США": [
        ("Нью-Йорк", "America/New_York"),
        ("Чикаго", "America/Chicago"),
        ("Денвер", "America/Denver"),
        ("Лос-Анджелес", "America/Los_Angeles"),
    ]
}