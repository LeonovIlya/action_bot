import logging
import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext


# декоратор обработки ошибок при обработке message
def error_handler_message(function):
    async def wrapper(message, state):
        try:
            result = await function(message, state)
            return result
        except Exception as error:
            await message.answer(
                text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!')
            logging.error('Message handler error: %s , function: %s, user: %s, '
                         'text: %s',
                         repr(error), function.__name__,
                         message.from_user.id, message.text)
    return wrapper


# декоратор обработки ошибок при обработке callback
def error_handler_callback(function):
    async def wrapper(callback, state):
        try:
            await function(callback, state)
        except Exception as error:
            await callback.message.answer(
                text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!')
            logging.error('Callback handler error: %s , function: %s, '
                         'user: %s, data: %s',
                         repr(error), function.__name__,
                         callback.from_user.id, callback.data)
    return wrapper
