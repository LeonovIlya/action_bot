from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState

RATINGS_DICT = {'[%_pss]': '% PSS', '[%_osa]': '% OSA', '[%_tt]': '% TT',\
               '[%_visits]': '% Visits'}


async def get_result_rating(rating_name: str,
                            select_name: str,
                            tg_id: int):
    return await db.get_one(
        query=await queries.ratings_query(
            column_name=rating_name,
            where_name=select_name,
            where_value=await db.get_one(
                await queries.get_value_by_tg_id(select_name),
                tg_id=tg_id)),
        tg_id=tg_id)


async def ratings_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.ratings_menu_merch)
    await UserState.ratings_menu_mr.set()


async def ratings_mr(message: types.Message):
    tg_id = message.from_user.id

    for i in RATINGS_DICT.keys():
        result1 = await db.get_one(
            await queries.ratings_query_all(column_name=i),
            tg_id=tg_id)
        result2 = await get_result_rating(rating_name=i,
                                          select_name='region',
                                          tg_id=tg_id)
        result3 = await get_result_rating(rating_name=i,
                                          select_name='kas',
                                          tg_id=tg_id)
        result4 = await get_result_rating(rating_name=i,
                                          select_name='citimanager',
                                          tg_id=tg_id)
        await message.answer(text=f'<b>Ваше место по {RATINGS_DICT[i]}:</b>\n'
                                  f'<b>По КАС:</b> {result3}\n'
                                  f'<b>По СитиМенеджеру:</b> {result4}\n'
                                  f'<b>По региону:</b> {result2}\n'
                                  f'<b>По стране:</b> {result1}\n',
                             reply_markup=keyboards.back)


async def tests_results_mr(message: types.Message, state: FSMContext):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)
    await state.finish()


def register_handlers_ratings(dp: Dispatcher):
    dp.register_message_handler(ratings_menu,
                                text='Рейтинги📊')
    dp.register_message_handler(ratings_mr,
                                text='Мои рейтинги📊',
                                state=UserState.ratings_menu_mr)
    dp.register_message_handler(tests_results_mr,
                                text='Результаты тестов📋',
                                state=UserState.ratings_menu_mr)
