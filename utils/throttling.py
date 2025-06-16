import asyncio
from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from typing import Union

from config import config


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple Throttling middleware from aiogram documentation
    """
    def __init__(self,
                 limit=config.RATE_LIMIT,
                 key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def throttle(self,
                       target: Union[types.Message, types.CallbackQuery]):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler,
                            'throttling_rate_limit',
                            self.rate_limit)
            key = getattr(handler,
                          'throttling_key',
                          f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=float(limit))
        except Throttled as t:
            await self.target_throttled(target, t, dispatcher, key)
            raise CancelHandler()

    @staticmethod
    async def target_throttled(
            target: Union[types.Message, types.CallbackQuery],
            throttled: Throttled, dispatcher: Dispatcher, key: str):
        msg = target.message if isinstance(target, types.CallbackQuery) \
            else target
        delta = throttled.rate - throttled.delta
        if throttled.exceeded_count == 5:
            await msg.reply('Вы слишком часто отправляете запросы боту!')
            return
        elif throttled.exceeded_count == 10:
            await msg.reply(f'⚠ Вы превысили лимит запросов к боту! Ждите, '
                            f'пока не пройдет {round(delta, 3)} секунд')
            return
        await asyncio.sleep(delta)

    async def on_process_message(self, message, data):
        await self.throttle(message)

    async def on_process_callback_query(self, call, data):
        await self.throttle(call)


def rate_limit(limit: int, key=None):
    """
    Decorator for configuring rate limit and key in different functions.

    :param limit:
    :param key:
    :return:
    """
    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func
    return decorator
