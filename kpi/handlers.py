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

KPI = ['PSS:', 'OSA:', 'TT:', 'VISITS:', 'ISA-OSA:']


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
            text=f'```\n'
                 f'        план|    факт|результат\n'
                 f'{KPI[0]:<4}'
                 f'{query[0]:>8.2%}|{query[1]:>8.2%}|{query[2]:>8.2%}\n'
                 f'{KPI[1]:<4}'
                 f'{query[3]:>8.2%}|{query[4]:>8.2%}|{query[5]:>8.2%}\n'
                 f'{KPI[2]:<4}'
                 f'{query[6]:>8}|{query[7]:>8}|{query[8]:>8.2%}\n'
                 f'{KPI[3]:<7}'
                 f'{query[9]:>5}|{query[10]:>8}|{query[11]:>8.2%}\n'
                 f'{KPI[4]:<7}{query[12]:>22}\n'
                 f'```',
            reply_markup=keyboards.back,
            parse_mode='MarkdownV2')
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
                address = address\
                    .replace("_", "\\_")\
                    .replace(".", "\\.")\
                    .replace("-", "\\-")\
                    .replace("*", "\\*")\
                    .replace("@", "\\@")\
                    .replace("&", "\\&")
                mr = query[2].replace("_", "\\_")
                await message.answer(
                    text=f'*TT №* {tt_num}\n'
                         f'*Сеть:* {query[1]}\n'
                         f'**Адрес:** {address}\n'
                         f'*MR:* {mr}\n'
                         f'*KAS:* {query[3]}\n\n'
                         f'```\n'
                         f'        план|    факт|результат\n'
                         f'{KPI[0]:<4}'
                         f'{query[4]:>8.2%}|{query[5]:>8.2%}|{query[6]:>8.2%}\n'
                         f'{KPI[1]:<4}'
                         f'{query[7]:>8.2%}|{query[8]:>8.2%}|{query[9]:>8.2%}\n'
                         f'{KPI[2]:<4}'
                         f'{query[10]:>8}|{query[11]:>8}|{query[12]:>8.2%}\n'
                         f'{KPI[3]:<7}'
                         f'{query[13]:>5}|{query[14]:>8}|{query[15]:>8.2%}\n'
                         f'{KPI[4]:<7}{query[16]:>22}\n'
                         f'```',
                    reply_markup=keyboards.back,
                    parse_mode='MarkdownV2')
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
