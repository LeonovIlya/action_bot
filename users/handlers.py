from aiogram import types, Dispatcher

from loader import db
from utils import keyboards, queries
from utils.states import UserState


# стартовое меню бота
async def start_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.start_menu_merch)
    auth_level = await db.get_one(await queries.get_value_by_tg_id('position'),
                                  tg_id=message.from_user.id)
    print(auth_level)

    match auth_level:
        case 'mr':
            await UserState.auth_mr.set()
        case 'kas':
            await UserState.auth_kase.set()
        case 'citimanager':
            await UserState.auth_citimanager.set()


# компануем в обработчик
def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start_menu,
                                text="Назад",
                                state='*')
