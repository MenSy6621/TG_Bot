import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN

from scheduler.scheduler import scheduler

from handlers.start import router as start_router
from handlers.tasks import router as tasks_router
from handlers.interval import router as interval_router
from handlers.settings import router as settings_router



from handlers.timezone import router as timezone_router


from database.queries import init_db


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    await init_db()

    bot = Bot(BOT_TOKEN)

    dp = Dispatcher()

    dp.include_router(timezone_router)
    dp.include_router(start_router)
    dp.include_router(tasks_router)
    dp.include_router(settings_router)
    dp.include_router(interval_router)


    scheduler.start()

    logging.info("Scheduler started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())