from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from users.handlers import get_value_by_tgig
from utils import decorators, keyboards, queries
from utils.states import UserState

RATINGS_TUPLE = (('[%_pss]', '% PSS', 'DESC'),
                 ('[%_osa]', '% OSA', 'DESC'),
                 ('[%_tt]', '% TT', 'DESC'),
                 ('[%_visits]', '% Visits', 'DESC'),
                 ('isa_osa', 'ISA-OSA', 'ASC'))


async def get_result_rating(column_name: str,
                            sort_type: str,
                            position: str,
                            where_name: str,
                            tg_id: int):
    return await db.get_one(
        await queries.ratings_query(
            column_name=column_name,
            sort_type=sort_type,
            position=position,
            where_name=where_name,
            where_value=await get_value_by_tgig(
                value=where_name,
                tg_id=tg_id)),
        tg_id=tg_id)


async def ratings_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.ratings_menu_mr)
    await UserState.ratings_menu_mr.set()


@decorators.error_handler_message
async def ratings_mr(message: types.Message, state: FSMContext):
    tg_id = int(message.from_user.id)
    position = await get_value_by_tgig(
        value='position',
        tg_id=tg_id)
    match position:
        case 'mr':
            for i in RATINGS_TUPLE:
                result1 = await db.get_one(
                    await queries.ratings_query_all(
                        column_name=i[0],
                        sort_type=i[2],
                        position=position),
                    tg_id=tg_id)
                result2 = await get_result_rating(
                    column_name=i[0],
                    sort_type=i[2],
                    position=position,
                    where_name='region',
                    tg_id=tg_id)
                result3 = await get_result_rating(
                    column_name=i[0],
                    sort_type=i[2],
                    position=position,
                    where_name='citimanager',
                    tg_id=tg_id)
                result4 = await get_result_rating(
                    column_name=i[0],
                    sort_type=i[2],
                    position=position,
                    where_name='kas',
                    tg_id=tg_id)
                if (result1 or result2 or result3 or result4) is not None:
                    await message.answer(
                        text=f'<b>Ваше место по {i[1]}:</b>\n'
                             f'<b>По КАС:</b> '
                             f'{result4[0]} из {result4[1]}\n'
                             f'<b>По СитиМенеджеру:</b> '
                             f'{result3[0]} из {result3[1]}\n'
                             f'<b>По региону:</b> '
                             f'{result2[0]} из {result2[1]}\n'
                             f'<b>По стране:</b> '
                             f'{result1[0]} из {result1[1]}\n',
                        reply_markup=keyboards.back)
                else:
                    await message.answer(
                        text=f'<b>Ваш показатель по {i[1]} = 0, в рейтинге '
                             f'не учитывается. '
                             f'</b>\n',
                        reply_markup=keyboards.back)
        case 'kas':
            for i in RATINGS_TUPLE:
                result1 = await db.get_one(
                    await queries.ratings_query_all(
                        column_name=i[0],
                        sort_type=i[2],
                        position=position),
                    tg_id=tg_id)
                result2 = await get_result_rating(
                    column_name=i[0],
                    sort_type=i[2],
                    position=position,
                    where_name='region',
                    tg_id=tg_id)
                result3 = await get_result_rating(
                    column_name=i[0],
                    sort_type=i[2],
                    position=position,
                    where_name='citimanager',
                    tg_id=tg_id)
                if (result1 or result2 or result3) is not None:
                    await message.answer(
                        text=f'<b>Ваше место по {i[1]}:</b>\n'
                             f'<b>По СитиМенеджеру:</b> '
                             f'{result3[0]} из {result3[1]}\n'
                             f'<b>По региону:</b> '
                             f'{result2[0]} из {result2[1]}\n'
                             f'<b>По стране:</b> '
                             f'{result1[0]} из {result1[1]}\n',
                        reply_markup=keyboards.back)
                else:
                    await message.answer(
                        text=f'<b>Ваш показатель по {i[1]} = 0, в рейтинге '
                             f'не учитывается. '
                             f'</b>\n',
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
