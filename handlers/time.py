from aiogram import Router, types
from aiogram.filters import Command

from database.queries import add_alert_time, remove_alert_time, get_alert_times
from BOT.services.parser import schedule

router = Router()
@router.message(Command("settime"))
async def cmd_settime(m: types.Message):
    uid = m.from_user.id
    arg = m.text.partition(" ")[2].strip()
    try:
        hh, mm = map(int, arg.split(":"))
        if not (0 <= hh < 24 and 0 <= mm < 60):
            raise ValueError
        add_alert_time(uid, hh, mm)
        await schedule(uid)
        await m.answer(f"✅ Добавлено время {hh:02d}:{mm:02d}")
    except Exception:
        await m.answer("⚠️ Формат: /settime чч:мм\nПример: /settime 09:00")

@router.message(Command("removetime"))
async def cmd_removetime(m: types.Message):
    uid = m.from_user.id
    arg = m.text.partition(" ")[2].strip()
    try:
        hh, mm = map(int, arg.split(":"))
        remove_alert_time(uid, hh, mm)
        await schedule(uid)
        await m.answer(f"🗑 Удалено время {hh:02d}:{mm:02d}")
    except:
        await m.answer("⚠️ Формат: /removetime чч:мм")

@router.message(Command("listtime"))
async def cmd_listtime(m: types.Message):
    uid = m.from_user.id
    times = get_alert_times(uid)
    msg = ["🕒 Времена уведомлений:"]
    for i, t in enumerate(times, start=1):
        msg.append(f"{i}. {t.strftime('%H:%M')}")
    await m.answer("\n".join(msg))