from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState


async def some_function(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.main_menu)


def register_handlers_shop(dp: Dispatcher):
    dp.register_message_handler(some_function,
                                text='Магазин🏦',
                                state='*')
