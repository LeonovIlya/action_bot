import asyncio
import hashlib

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import config
from loader import db
from utils import decorators, keyboards, queries
from utils.states import UserState


async def adapt_start_await(callback: types.CallbackQuery, state: FSMContext):
    print(callback.data)
    await callback.bot.answer_callback_query(callback.id)
    await callback.message.delete()
    await callback.message.answer(text='Ok! Вернемся к этому вопросу через 2 рабочих дня!')



# компануем в обработчик
def register_handlers_adaptation(dp: Dispatcher):
    dp.register_callback_query_handler(
        adapt_start_await,
        text_startswith="adapt_start_await_",
        state='*')
