from aiogram import types

from .models import User


async def get_user(user: types.User):
    u = await User.filter(tg_id=user.id).first()
    if not u:
        u = await User.create(
            tg_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            tg_username=user.username
        )
    return u
