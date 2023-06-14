from aiogram import types, Dispatcher

from utils import keyboards
from utils.states import UserState


# стартовое меню бота
async def start_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.start_menu_merch)


async def stuff_merch_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:', reply_markup=keyboards.stuff_menu_merch)


# компануем в обработчик
def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start_menu, text="Назад", state='*')
    dp.register_message_handler(stuff_merch_menu, text="Инструменты🛠", state='*')
