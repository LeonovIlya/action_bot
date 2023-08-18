from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from users.handlers import get_value_by_tgig
from utils import decorators, keyboards, queries
from utils.states import UserState

RATINGS_DICT = {'[%_pss]': '% PSS', '[%_osa]': '% OSA', '[%_tt]': '% TT',
                '[%_visits]': '% Visits', 'isa_osa': 'ISA-OSA'}


async def get_result_rating(rating_name: str,
                            position: str,
                            select_name: str,
                            tg_id: int):
    try:
        return await db.get_one(
            await queries.ratings_query(
                column_name=rating_name,
                position=position,
                where_name=select_name,
                where_value=await get_value_by_tgig(
                    value=select_name,
                    table='users',
                    tg_id=tg_id
                )),
            tg_id=tg_id
        )
    except Exception as error:
        logging.info(f'Error: {error}')
        raise error


async def ratings_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.ratings_menu_mr)
    await UserState.ratings_menu_mr.set()


@decorators.error_handler_message
async def ratings_mr(message: types.Message, state: FSMContext):
    tg_id = int(message.from_user.id)
    position = await get_value_by_tgig(
        value='position',
        table='users',
        tg_id=tg_id)
    match position:
        case 'mr':
            for i, k in RATINGS_DICT.items():
                result1 = await db.get_one(
                    await queries.ratings_query_all(
                        column_name=i,
                        position=position),
                    tg_id=tg_id)
                result2 = await get_result_rating(
                    rating_name=i,
                    position=position,
                    select_name='region',
                    tg_id=tg_id)
                result3 = await get_result_rating(
                    rating_name=i,
                    position=position,
                    select_name='kas',
                    tg_id=tg_id)
                result4 = await get_result_rating(
                    rating_name=i,
                    position=position,
                    select_name='citimanager',
                    tg_id=tg_id)
                await message.answer(
                    text=f'<b>Ваше место по {k}:</b>\n'
                         f'<b>По КАС:</b> '
                         f'{result3[0]} из {result3[1]}\n'
                         f'<b>По СитиМенеджеру:</b> '
                         f'{result4[0]} из {result4[1]}\n'
                         f'<b>По региону:</b> '
                         f'{result2[0]} из {result2[1]}\n'
                         f'<b>По стране:</b> '
                         f'{result1[0]} из {result1[1]}\n',
                    reply_markup=keyboards.back)
        case 'kas':
            for i, k in RATINGS_DICT.items():
                result1 = await db.get_one(
                    await queries.ratings_query_all(
                        column_name=i,
                        position=position),
                    tg_id=tg_id)
                result2 = await get_result_rating(
                    rating_name=i,
                    position=position,
                    select_name='region',
                    tg_id=tg_id)
                result4 = await get_result_rating(
                    rating_name=i,
                    position=position,
                    select_name='citimanager',
                    tg_id=tg_id)
                await message.answer(
                    text=f'<b>Ваше место по {k}:</b>\n'
                         f'<b>По СитиМенеджеру:</b> '
                         f'{result4[0]} из {result4[1]}\n'
                         f'<b>По региону:</b> '
                         f'{result2[0]} из {result2[1]}\n'
                         f'<b>По стране:</b> '
                         f'{result1[0]} из {result1[1]}\n',
                    reply_markup=keyboards.back)


async def tests_results_mr(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


def register_handlers_ratings(dp: Dispatcher):
    dp.register_message_handler(
        ratings_menu,
        text='Назад↩',
        state=UserState.ratings_menu_mr)
    dp.register_message_handler(
        ratings_menu,
        text='Рейтинги📊',
        state=(UserState.auth_mr,
               UserState.auth_kas))
    dp.register_message_handler(
        ratings_mr,
        text='Мои рейтинги📊',
        state=UserState.ratings_menu_mr)
    dp.register_message_handler(
        tests_results_mr,
        text='Результаты тестов📋',
        state=UserState.ratings_menu_mr)
