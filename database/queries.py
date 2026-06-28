from database.db import get_connection


async def init_db():

    async with get_connection() as db:
        # =========================
        # USERS
        # =========================

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (

                user_id INTEGER PRIMARY KEY,

                timezone TEXT,

                reminder_interval INTEGER DEFAULT 30

            )
            """
        )
        await db.commit()

        # =========================
        # TASKS
        # =========================
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                text TEXT NOT NULL,

                type TEXT NOT NULL,

                interval_minutes INTEGER,

                period TEXT,

                remind_time TEXT,

                end_time TEXT,

                timezone TEXT,

                job_id TEXT UNIQUE,

                active INTEGER DEFAULT 1
            )
            """
        )

        await db.commit()


# =========================================================
# USERS
# =========================================================

async def set_user_timezone(user_id: int, tz_name: str):

    async with get_connection() as db:

        await db.execute(
            """
            INSERT INTO users (

                user_id,
                timezone

            )
            VALUES (?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                timezone = excluded.timezone
            """,
            (
                user_id,
                tz_name
            )
        )

        await db.commit()

async def set_user_interval(
    user_id,
    interval
):

    async with get_connection() as db:

        await db.execute(
            """
            INSERT INTO users (

                user_id,
                reminder_interval

            )
            VALUES (?, ?)

            ON CONFLICT(user_id)
            DO UPDATE SET
                reminder_interval =
                excluded.reminder_interval
            """,
            (
                user_id,
                interval
            )
        )

        await db.commit()

async def get_user_interval(
    user_id
):

    async with get_connection() as db:

        cursor = await db.execute(
            """
            SELECT reminder_interval
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        row = await cursor.fetchone()

        if row and row[0] is not None:

            return row[0]

        return 30

async def get_user_timezone(user_id: int):

    async with get_connection() as db:

        cursor = await db.execute(
            """
            SELECT timezone
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        row = await cursor.fetchone()

        if row:

            return row[0]

        return None


# =========================================================
# TASKS
# =========================================================


async def add_task(
    user_id,
    text,
    task_type,
    interval_minutes,
    period,
    remind_time,
    end_time,
    timezone,
    job_id
):

    async with get_connection() as db:

        cursor = await db.execute(
            """
            INSERT INTO tasks (

                user_id,
                text,
                type,
                interval_minutes,
                period,
                remind_time,
                end_time,
                timezone,
                job_id

            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                text,
                task_type,
                interval_minutes,
                period,
                remind_time,
                end_time,
                timezone,
                job_id
            )
        )

        await db.commit()

        return cursor.lastrowid


async def get_tasks(user_id):

    async with get_connection() as db:

        cursor = await db.execute(
            """
            SELECT
                id,
                user_id,
                text,
                type,
                interval_minutes,
                period,
                remind_time,
                end_time,
                timezone,
                job_id

            FROM tasks

            WHERE user_id = ?

            ORDER BY id DESC
            """,
            (user_id,)
        )

        return await cursor.fetchall()


async def get_task(task_id, user_id):

    async with get_connection() as db:

        cursor = await db.execute(
            """
            SELECT
                id,
                user_id,
                text,
                type,
                interval_minutes,
                period,
                remind_time,
                end_time,
                timezone,
                job_id

            FROM tasks

            WHERE id = ?
            AND user_id = ?
            """,
            (
                task_id,
                user_id
            )
        )

        return await cursor.fetchone()


async def delete_task(task_id, user_id):

    async with get_connection() as db:

        await db.execute(
            """
            DELETE FROM tasks

            WHERE id = ?
            AND user_id = ?
            """,
            (
                task_id,
                user_id
            )
        )

        await db.commit()

async def pause_task(
    task_id,
    user_id
):

    async with get_connection() as db:

        await db.execute(
            """
            UPDATE tasks

            SET paused = 1

            WHERE id = ?
            AND user_id = ?
            """,
            (
                task_id,
                user_id
            )
        )

        await db.commit()

async def unpause_task(
    task_id,
    user_id
):

    async with get_connection() as db:

        await db.execute(
            """
            UPDATE tasks

            SET paused = 0

            WHERE id = ?
            AND user_id = ?
            """,
            (
                task_id,
                user_id
            )
        )

        await db.commit()

# =========================================================
# OPTIONAL
# =========================================================

async def update_task_job_id(
    task_id,
    user_id,
    job_id
):

    async with get_connection() as db:

        await db.execute(
            """
            UPDATE tasks

            SET job_id = ?

            WHERE id = ?
            AND user_id = ?
            """,
            (
                job_id,
                task_id,
                user_id
            )
        )

        await db.commit()
