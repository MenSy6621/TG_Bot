import logging

from aiogram import Router
from aiogram.types import CallbackQuery

from apscheduler.jobstores.base import (
    JobLookupError
)

from scheduler.scheduler import scheduler

from database.queries import (
    get_task
)


router = Router()

logger = logging.getLogger(__name__)


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

        job_id = task[9]

        if not job_id:

            await call.answer(
                "Уведомление уже остановлено"
            )

            return

        try:

            scheduler.remove_job(
                job_id
            )

        except JobLookupError:

            logger.warning(
                f"Job {job_id} not found"
            )

        await call.message.edit_text(
            f"⏸ Уведомления остановлены\n\n"
            f"{task[2]}"
        )

        await call.answer(
            "Done"
        )

        logger.info(
            f"User {call.from_user.id} "
            f"stopped task #{task_id}"
        )

    except Exception as e:

        logger.exception(e)

        await call.answer(
            "Ошибка"
        )