from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState


async def kpi_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.kpi_menu_merch)
    await UserState.kpi_menu_mr.set()


async def kpi_mr(message: types.Message):
    user_tg_id = message.from_user.id
    query = await db.get_one(queries.kpi_mr_query,
                             tg_id=int(user_tg_id))
    await message.answer(text=f'<b>Ваш KPI (план | факт | выполнение):</b>\n'
                              f'<b><u>PSS:</u></b> {query[0]:.2%} |'
                              f' {query[1]:.2%}'
                              f' | {query[2]:.2%}\n'
                              f'<b><u>OSA:</u></b> {query[3]:.2%} |'
                              f' {query[4]:.2%} |'
                              f' {query[5]:.2%}\n'
                              f'<b><u>TT:</u></b> {query[6]} | {query[7]} |'
                              f' {query[8]:.2%}\n'
                              f'<b><u>Visits:</u></b> {query[9]} |'
                              f' {query[10]} |'
                              f' {query[11]:.2%}\n'
                              f'<b><u>ISA-OSA:</u></b> {query[12]}',
                         reply_markup=keyboards.back)


async def kpi_tt(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


def register_handlers_kpi(dp: Dispatcher):
    dp.register_message_handler(kpi_menu,
                                text='Назад↩',
                                state=UserState.kpi_menu_mr)
    dp.register_message_handler(kpi_menu,
                                text='KPI📈',
                                state='*')
    dp.register_message_handler(kpi_mr,
                                text='Мой KPI📈',
                                state=UserState.kpi_menu_mr)
    dp.register_message_handler(kpi_tt,
                                text='KPI TT🏬',
                                state=UserState.kpi_menu_mr)
