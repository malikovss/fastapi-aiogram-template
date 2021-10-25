import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler, current_handler, Handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


def rate_limit(limit: float, key=None):
    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=.8, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_callback_query(self, query: types.CallbackQuery, data: dict):
        if query.inline_message_id:
            return
        handler: Handler = current_handler.get()
        # Get dispatcher from context
        dispatcher = Dispatcher.get_current()
        # If handler was configured, get rate limit and key from handler
        notify = False
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', None)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
            if limit:
                notify = True
            else:
                limit = self.rate_limit
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            print('key:', key)
            if notify:
                await query.answer('Biroz kuting...')
            else:
                await query.answer()
            delta = t.rate - t.delta
            await asyncio.sleep(delta)
            raise CancelHandler()

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        # Use Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as throttled:
            delta = throttled.rate - throttled.delta
            await asyncio.sleep(delta)
            raise CancelHandler()
