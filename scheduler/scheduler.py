from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

import pytz


scheduler = AsyncIOScheduler(
    timezone= pytz.UTC,
    jobstores={
        "default": SQLAlchemyJobStore(
            url="sqlite:///jobs.sqlite"
        )
    }
)