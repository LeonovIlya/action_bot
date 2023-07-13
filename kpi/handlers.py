import re
import logging
import aiofiles

from aiopath import AsyncPath
from aiogram import Dispatcher, types

from loader import db
from utils import keyboards, queries
from utils.states import UserState

R_STR = r'(^\d{6},)|(\w+\sобл,)|(\w+-\w+\sр-н,)|(\w+\sр-н,)|(\w+\sрн,' \
        r')|(\s№\s)|(\sг,)'


async def kpi_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.kpi_menu)
    await UserState.kpi_menu.set()


async def kpi_mr(message: types.Message):
    try:
        query = await db.get_one(
            queries.KP_MR_QUERY,
            tg_id=int(message.from_user.id))
        await message.answer(
            text=f'<b>Ваш KPI (план | факт | выполнение):</b>\n'
                 f'<b><u>PSS:</u></b> '
                 f'{query[0]:.2%} | {query[1]:.2%} | {query[2]:.2%}\n'
                 f'<b><u>OSA:</u></b> '
                 f'{query[3]:.2%} | {query[4]:.2%} | {query[5]:.2%}\n'
                 f'<b><u>TT:</u></b> '
                 f'{query[6]} | {query[7]} | {query[8]:.2%}\n'
                 f'<b><u>Visits:</u></b> '
                 f'{query[9]} | {query[10]} | {query[11]:.2%}\n'
                 f'<b><u>ISA-OSA:</u></b> {query[12]}',
            reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(
            text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def kpi_tt(message: types.Message):
    await message.answer(
        text='Введите 7-и значный номер ТТ:',
        reply_markup=keyboards.back)
    await UserState.kpi_search_tt.set()


async def kpi_search_tt(message: types.Message):
    tt_num = re.sub(r'\s', '', str(message.text))
    if re.match(r'\d{7}', tt_num) and len(tt_num) == 7:
        try:
            query = await db.get_one(
                queries.KPI_TT_QUERY,
                tt_num=tt_num)
            if query:
                address = re.sub(R_STR, '', query[0])
                await message.answer(
                    text=f'<b>TT № {tt_num}:</b>\n'
                         f'<b>Сеть:</b> {query[1]}\n'
                         f'<b>Адрес:</b> {address}\n'
                         f'<b>MR:</b> {query[2]}\n'
                         f'<b>KAS:</b> {query[3]}\n\n'
                         f'<b>      план | факт | выполнение</b>\n'
                         f'<b><u>PSS:</u></b> '
                         f'{query[4]:.2%} | {query[5]:.2%} | {query[6]:.2%}\n'
                         f'<b><u>OSA:</u></b> '
                         f'{query[7]:.2%} | {query[8]:.2%} | {query[9]:.2%}\n'
                         f'<b><u>TT:</u></b> '
                         f'{query[10]} | {query[11]} | {query[12]:.2%}\n'
                         f'<b><u>VISITS:</u></b> '
                         f'{query[13]} | {query[14]} | {query[15]:.2%}\n'
                         f'<b><u>ISA-OSA:</u></b> {query[16]}',
                    reply_markup=keyboards.back)
            else:
                await message.answer(
                    text='❗ ТТ с таким номером не найдена!\n'
                         'Попробуйте еще раз!',
                    reply_markup=keyboards.back)
        except Exception as error:
            await message.answer(
                text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!')
            logging.info(
                f'Error: {error}, user: {int(message.from_user.id)}')

    else:
        await message.answer(
            text='❗ Номер ТТ не соответствует формату ввода!\n'
                 'Введите еще раз!',
            reply_markup=keyboards.back)


async def get_bonus_info(message: types.Message):
    file_link = './files/kpi/bonus.jpg'
    file = AsyncPath(file_link)
    if await file.is_file():
        await message.answer_chat_action(
            action='upload_document')
        async with aiofiles.open(file_link, 'rb') as photo:
            await message.answer_photo(
                photo=photo,
                reply_markup=keyboards.back)
    else:
        await message.answer(
            text='Файл не найден!',
            reply_markup=keyboards.back)


def register_handlers_kpi(dp: Dispatcher):
    dp.register_message_handler(
        kpi_menu,
        text='Назад↩',
        state=(UserState.kpi_menu,
               UserState.kpi_search_tt))
    dp.register_message_handler(
        kpi_menu,
        text='KPI📈',
        state=(UserState.auth_mr,
               UserState.auth_kas,
               UserState.auth_cm))
    dp.register_message_handler(
        kpi_mr,
        text='Мой KPI📈',
        state=UserState.kpi_menu)
    dp.register_message_handler(
        kpi_tt,
        text='KPI TT🏬',
        state=UserState.kpi_menu)
    dp.register_message_handler(
        kpi_search_tt,
        state=UserState.kpi_search_tt)
    dp.register_message_handler(
        get_bonus_info,
        text='Информация по бонусу💰',
        state=UserState.kpi_menu)
