from typing import Dict, Any

from aiogram import Dispatcher, Bot
from aiogram.types import Update
from fastapi import APIRouter, Body, Response, status, BackgroundTasks

from app.bot.core.middlewares import ThrottlingMiddleware
from app.bot.handlers import dp
from app.core import settings

router = APIRouter()


async def feed_update(update: dict):
    telegram_update = Update(**update)
    Bot.set_current(dp.bot)
    Dispatcher.set_current(dp)
    await dp.process_update(telegram_update)


@router.post(settings.WEBHOOK_PATH, include_in_schema=False)
async def telegram_post(background_tasks: BackgroundTasks, update: Dict[str, Any] = Body(...)) -> Response:
    background_tasks.add_task(feed_update, update)
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.on_event('startup')
async def on_startup() -> None:
    Bot.set_current(dp.bot)
    Dispatcher.set_current(dp)
    dp.middleware.setup(ThrottlingMiddleware())
    current_url = (await dp.bot.get_webhook_info())["url"]
    if current_url != settings.WEBHOOK_URL:
        await dp.bot.set_webhook(url=settings.WEBHOOK_URL)
    if not settings.DEBUG:
        await dp.bot.send_message(settings.ADMIN, "Bot ishlashni boshladi.")


@router.on_event('shutdown')
async def on_shutdown() -> None:
    await dp.storage.close()
    await dp.storage.wait_closed()
    await dp.bot.session.close()
