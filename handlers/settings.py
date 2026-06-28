import logging

from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from aiogram.fsm.state import (
    StatesGroup,
    State
)

from aiogram.fsm.context import (
    FSMContext
)

from aiogram.filters import Command

from apscheduler.jobstores.base import (
    JobLookupError
)

from scheduler.scheduler import scheduler


from database.queries import (
    get_task,
    get_tasks,
    delete_task
)

from datetime import (
    datetime,
    timedelta
)

import pytz

router = Router()

logger = logging.getLogger(__name__)
# =========================================================
# FSM
# =========================================================

class DelayState(
    StatesGroup
):

    waiting_minutes = State()

# =========================================================
# DONE -> PAUSE
# =========================================================

@router.callback_query(
    lambda c: c.data.startswith("done:")
)
async def done_callback(
    call: CallbackQuery
):

    try:

        task_id = int(
            call.data.split(":")[1]
        )

        task = await get_task(
            task_id,
            call.from_user.id
        )

        if not task:

            await call.answer(
                "Задача не найдена"
            )
            return

        task_type = task[3]
        job_id = task[9]

        # ==========================================
        # ONE_TIME -> DELETE
        # ==========================================

        if task_type == "one_time":

            try:

                scheduler.remove_job(
                    job_id
                )

            except JobLookupError:

                pass
                
            await delete_task(
                task_id,
                call.from_user.id
            )

            await call.message.edit_text(
                f"✅ Выполнено\n\n"
                f"{task[2]}"
            )

            await call.answer(
                "Удалено"
            )

        # ==========================================
        # UNTIL -> CHOICE
        # ==========================================

        elif task_type == "until":

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📅 Завтра",
                            callback_data=f"tomorrow:{task_id}"
                        ),
                        InlineKeyboardButton(
                            text="🗑 Delete",
                            callback_data=f"delete:{task_id}"
                        )
                    ]
                ]
            )

            await call.message.edit_text(
                f"⏰ {task[2]}\n\n"
                f"Что сделать?",
                reply_markup=keyboard
            )

            await call.answer()

        # ==========================================
        # PERIODIC -> NEXT TRIGGER
        # ==========================================

        else:

            try:

                scheduler.pause_job(
                    job_id
                )

            except JobLookupError:

                logger.warning(
                    f"Job {job_id} not found"
                )

            await call.message.edit_text(
                f"⏸ Приостановлено\n\n"
                f"{task[2]}"
            )

            await call.answer(
                "Done"
            )

        logger.info(
            f"User {call.from_user.id} "
            f"done task #{task_id}"
        )

    except Exception as e:

        logger.exception(e)

        await call.answer(
            "Ошибка"
        )

@router.callback_query(
    lambda c: c.data.startswith("tomorrow:")
)
async def tomorrow_callback(
    call: CallbackQuery
):

    task_id = int(
        call.data.split(":")[1]
    )

    task = await get_task(
        task_id,
        call.from_user.id
    )

    if not task:
        return

    job_id = task[9]
    timezone = task[8]

    tz = pytz.timezone(
        timezone
    )

    next_run = (
        datetime.now(tz)
        + timedelta(days=1)
    )

    scheduler.modify_job(
        job_id,
        next_run_time=next_run
    )

    await call.message.edit_text(
        "📅 Перенесено на завтра"
    )

    await call.answer()

# =========================================================
# LIST WITH STATUS
# =========================================================
@router.callback_query(
    lambda c: c.data.startswith("delete:")
)
async def delete_until_callback(
    call: CallbackQuery
):

    task_id = int(
        call.data.split(":")[1]
    )

    task = await get_task(
        task_id,
        call.from_user.id
    )

    if not task:
        return

    job_id = task[9]

    try:
        scheduler.remove_job(job_id)
    
    except JobLookupError:
        logger.warning(
            f"Job {job_id} not found"
        )

    await delete_task(
        task_id,
        call.from_user.id
    )

    await call.message.edit_text(
        "🗑 Удалено"
    )

    await call.answer()

@router.message(Command("list"))
async def list_handler(message: Message):

    try:

        tasks = await get_tasks(
            message.from_user.id
        )

        if not tasks:

            await message.answer(
                "📭 У вас нет задач"
            )

            return

        text = "📋 Ваши задачи:\n\n"

        for task in tasks:

            task_id = task[0]
            task_text = task[2]
            task_type = task[3]

            interval_minutes = task[4]
            period = task[5]
            remind_time = task[6]
            end_time = task[7]
            timezone = task[8]

            text += (
                f"🆔 ID: {task_id}\n"
                f"📝 {task_text}\n"
            )

            # ==========================================
            # UNTIL
            # ==========================================

            if task_type == "until":

                text += (
                    f"⏱ Каждые: {interval_minutes} мин\n"
                    f"🕒 До: {end_time}\n"
                    f"🌍 {timezone}\n\n"
                )

            # ==========================================
            # ONE TIME
            # ==========================================

            elif task_type == "one_time":

                text += (
                    f"🕒 Время: {remind_time}\n"
                    f"🌍 {timezone}\n\n"
                )

            # ==========================================
            # PERIODIC
            # ==========================================

            elif task_type == "periodic":

                text += (
                    f"🔁 {period}\n"
                    f"🕒 {remind_time}\n"
                    f"🌍 {timezone}\n\n"
                )

        await message.answer(text)
    except Exception as e:

        logger.exception(e)

        await message.answer(
            "Ошибка"
        )

# =========================================================
# DELETE
# =========================================================

@router.message(Command("delete"))
async def delete_handler(
    message: Message
):

    try:

        args = message.text.replace(
            "/delete",
            "",
            1
        ).strip()

        if not args:

            await message.answer(
                "Укажите ID\n\n"
                "/delete 3"
            )
            return

        try:

            task_id = int(args)

        except ValueError:

            await message.answer(
                "ID должен быть числом"
            )
            return

        task = await get_task(
            task_id,
            message.from_user.id
        )

        if not task:

            await message.answer(
                "Задача не найдена"
            )
            return

        job_id = task[9]

        try:

            scheduler.remove_job(
                job_id
            )

        except JobLookupError:

            logger.warning(
                f"Job {job_id} not found"
            )

        await delete_task(
            task_id,
            message.from_user.id
        )

        await message.answer(
            f"🗑 Удалено\n\n"
            f"{task[2]}"
        )

        logger.info(
            f"User {message.from_user.id} "
            f"deleted task #{task_id}"
        )

    except Exception as e:

        logger.exception(e)

        await message.answer(
            "Ошибка"
        )

# =========================================================
# DELAY
# =========================================================

@router.callback_query(
    lambda c: c.data.startswith(
        "delay:"
    )
)
async def delay_callback(
    call: CallbackQuery
):

    task_id = int(
        call.data.split(":")[1]
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="15",
                    callback_data=f"d15:{task_id}"
                ),
                InlineKeyboardButton(
                    text="30",
                    callback_data=f"d30:{task_id}"
                ),
                InlineKeyboardButton(
                    text="60",
                    callback_data=f"d60:{task_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏ Custom",
                    callback_data=f"dcustom:{task_id}"
                )
            ]
        ]
    )

    await call.message.answer(
        "⏳ На сколько отложить?",
        reply_markup=keyboard
    )

    await call.answer()

@router.callback_query(
    lambda c:
        c.data.startswith("d15:")
        or c.data.startswith("d30:")
        or c.data.startswith("d60:")
)
async def fixed_delay_callback(
    call: CallbackQuery
):

    prefix, task_id = (
        call.data.split(":")
    )

    task_id = int(task_id)

    minutes = int(
        prefix[1:]
    )

    task = await get_task(
        task_id,
        call.from_user.id
    )

    if not task:
        return

    job_id = task[9]

    job = scheduler.get_job(
        job_id
    )

    if job is None:
        return

    next_run = (
        datetime.now(
            job.next_run_time.tzinfo
        )
        + timedelta(
            minutes=minutes
        )
    )

    scheduler.modify_job(
        job_id,
        next_run_time=next_run
    )

    await call.message.edit_text(
        f"⏳ Отложено на "
        f"{minutes} мин"
    )

    await call.answer()

@router.callback_query(
    lambda c: c.data.startswith(
        "dcustom:"
    )
)
async def custom_delay_callback(
    call: CallbackQuery,
    state: FSMContext
):

    task_id = int(
        call.data.split(":")[1]
    )

    await state.update_data(
        task_id=task_id
    )

    await state.set_state(
        DelayState.waiting_minutes
    )

    await call.message.answer(
        "⏳ Введите минуты"
    )

    await call.answer()
    
    # =========================================================
# CUSTOM DELAY FSM
# =========================================================

@router.message(
    DelayState.waiting_minutes
)
async def custom_delay_input(
    message: Message,
    state: FSMContext
):

    try:

        minutes = int(
            message.text
        )

        if minutes < 1:

            await message.answer(
                "Минимум 1 минута"
            )
            return

        data = await state.get_data()

        task_id = data[
            "task_id"
        ]

        task = await get_task(
            task_id,
            message.from_user.id
        )

        if not task:

            await message.answer(
                "Задача не найдена"
            )

            await state.clear()

            return

        job_id = task[9]

        job = scheduler.get_job(
            job_id
        )

        if job is None:

            await message.answer(
                "Job не найден"
            )

            await state.clear()

            return

        next_run = (
            datetime.now(
                job.next_run_time.tzinfo
            )
            + timedelta(
                minutes=minutes
            )
        )

        scheduler.modify_job(
            job_id,
            next_run_time=next_run
        )

        await message.answer(
            f"⏳ Отложено на "
            f"{minutes} мин"
        )

        await state.clear()

        logger.info(
            f"User {message.from_user.id} "
            f"custom delay "
            f"{task_id} "
            f"{minutes} min"
        )

    except ValueError:

        await message.answer(
            "Введите число"
        )