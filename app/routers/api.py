from fastapi import APIRouter

from . import telegram

router = APIRouter()

router.include_router(telegram.router)
