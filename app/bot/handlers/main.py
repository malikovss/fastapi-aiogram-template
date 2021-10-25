from aiogram import types

from app.bot.loader import dp


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.reply('Hello world!')
