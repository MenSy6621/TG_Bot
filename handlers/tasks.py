import logging
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from apscheduler.jobstores.base import JobLookupError

import pytz

from scheduler.scheduler import scheduler
from scheduler.jobs import send_reminder

from database.queries import (
    add_task,
    get_tasks,
    delete_task,
    get_task,
    get_user_timezone,
    update_task_job_id,
    get_user_interval
)

from datetime import timedelta

from services.parser import parse_reminder


router = Router()

logger = logging.getLogger(__name__)


@router.message(Command("add"))
async def add_task_handler(message: Message):

    try:

        args = message.text.replace(
            "/add",
            "",
            1
        ).strip()

        if not args:

            await message.answer(
                "❌ Укажите текст задачи\n\n"

                "Примеры:\n\n"

                "/add Пить воду в 22:00\n"
                "/add Тренировка каждый день в 18:00\n"
                "/add Пить воду до 22:00 каждые 30"
            )

            return

        parsed = parse_reminder(args)

        if not parsed:

            await message.answer(
                "❌ Неверный формат\n\n"

                "Примеры:\n\n"

                "/add Пить воду в 22:00\n"
                "/add Тренировка каждый день в 18:00\n"
                "/add Пить воду до 22:00 каждые 30"
            )

            return

        uid = message.from_user.id

        # ==================================================
        # USER TIMEZONE
        # ==================================================

        tz_name = await get_user_timezone(uid)

        if tz_name is None:

            await message.answer(
                "❌ Сначала выберите часовой пояс:\n\n"
                "/timezone"
            )

            return

        user_tz = pytz.timezone(tz_name)

        # ==================================================
        # UNTIL
        # ==================================================

        if parsed["type"] == "until":

            now = datetime.now(
                user_tz
            )

            # ==========================================
            # START
            # ==========================================

            if parsed["start_time"]:

                naive_start_datetime = datetime.strptime(
                    parsed["start_time"],
                    "%H:%M"
                )

                start_datetime = naive_start_datetime.replace(
                    year=now.year,
                    month=now.month,
                    day=now.day
                )

                start_datetime = user_tz.localize(
                    start_datetime
                )

            else:

                start_datetime = now

            # ==========================================
            # END
            # ==========================================

            naive_end_datetime = datetime.strptime(
                parsed["end_time"],
                "%H:%M"
            )

            end_datetime = naive_end_datetime.replace(
                year=now.year,
                month=now.month,
                day=now.day
            )

            end_datetime = user_tz.localize(
                end_datetime
            )

            # ==========================================
            # CROSS MIDNIGHT
            # ==========================================

            if end_datetime <= start_datetime:

                end_datetime += timedelta(
                    days=1
                )

            if start_datetime <= now and parsed["start_time"]:

                start_datetime += timedelta(
                    days=1
                )

            # ==========================================
            # TASK
            # ==========================================

            task_id = await add_task(
                user_id=uid,
                text=parsed["task"],
                task_type="until",
                interval_minutes=parsed["interval"],
                period=None,
                remind_time=parsed.get(
                    "start_time"
                ),
                end_time=parsed["end_time"],
                timezone=tz_name,
                job_id=None
            )

            job = scheduler.add_job(
                send_reminder,
                trigger="interval",
                minutes=parsed["interval"],
                start_date=start_datetime,
                end_date=end_datetime,
                timezone=user_tz,
                args=[
                    uid,
                    parsed["task"],
                    task_id
                ]
            )

            await update_task_job_id(
                task_id,
                uid,
                job.id
            )

            await message.answer(
                f"✅ Напоминание создано\n\n"
                f"🆔 ID: {task_id}\n"
                f"📝 {parsed['task']}\n"
                f"▶ С: "
                f"{parsed['start_time'] or 'сейчас'}\n"
                f"🕒 До: {parsed['end_time']}\n"
                f"⏱ Каждые: "
                f"{parsed['interval']} мин\n"
                f"🌍 {tz_name}"
            )

        # ==================================================
        # ONE TIME
        # ==================================================

        elif parsed["type"] == "one_time":

            now = datetime.now(user_tz)

            naive_run_date = datetime.strptime(
                parsed["time"],
                "%H:%M"
            )

            run_date = naive_run_date.replace(
                year=now.year,
                month=now.month,
                day=now.day
            )

            run_date = user_tz.localize(
                run_date
            )

            if run_date <= now:

                await message.answer(
                    "❌ Время уже прошло"
                )

                return
           
            repeat_minutes = await get_user_interval( 
                uid 
            )

            task_id = await add_task(
                user_id=uid,
                text=parsed["task"],
                task_type="one_time",
                interval_minutes=None,
                period=None,
                remind_time=parsed["time"],
                end_time=None,
                timezone=tz_name,
                job_id=None
            )

            job = scheduler.add_job(
                send_reminder,
                trigger="interval",
                minutes=repeat_minutes,
                start_date=run_date,
                timezone=user_tz,
                args=[
                    uid,
                    parsed["task"],
                    task_id
                ]
            )

            await update_task_job_id(
                task_id,
                uid,
                job.id
            )

            await message.answer(
                f"✅ Разовое напоминание создано\n\n"

                f"🆔 ID: {task_id}\n"
                f"📝 {parsed['task']}\n"
                f"🕒 Время: {parsed['time']}\n"
                f"🌍 {tz_name}"
            )

        # ==================================================
        # PERIODIC
        # ==================================================

        elif parsed["type"] == "periodic":

            hour, minute = map(
                int,
                parsed["time"].split(":")
            )

            repeat_minutes = await get_user_interval(
                uid
            )

            now = datetime.now(user_tz)

            start_date = now.replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )

            if start_date <= now:

                from datetime import timedelta

                start_date += timedelta(days=1)

            task_id = await add_task(
                user_id=uid,
                text=parsed["task"],
                task_type="periodic",
                interval_minutes=repeat_minutes,
                period=parsed["period"],
                remind_time=parsed["time"],
                end_time=None,
                timezone=tz_name,
                job_id=None
            )

            job = scheduler.add_job(
                send_reminder,
                trigger="interval",
                minutes=repeat_minutes,
                start_date=start_date,
                timezone=user_tz,
                args=[
                    uid,
                    parsed["task"],
                    task_id
                ]
            )

            await update_task_job_id(
                task_id,
                uid,
                job.id
            )

            await message.answer(
                f"✅ Периодическое напоминание создано\n\n"
                f"🆔 ID: {task_id}\n"
                f"📝 {parsed['task']}\n"
                f"⏱ Интервал: {repeat_minutes} мин\n"
                f"▶ Старт: {parsed['time']}\n"
                f"🌍 {tz_name}"
            )

    except Exception as e:

        logger.exception(e)

        await message.answer(
            "❌ Ошибка при создании задачи"
        )
