from fastapi import APIRouter

from . import telegram, authentication

router = APIRouter()

router.include_router(telegram.router)
router.include_router(authentication.router, prefix='/login')
