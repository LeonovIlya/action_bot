import re
import aiofiles

from datetime import datetime as dt
from aiopath import AsyncPath
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import decorators, keyboards, queries
from utils.states import UserState

R_STR = r'(^\d{6},)|(\w+\sобл,)|(\w+-\w+\sр-н,)|(\w+\sр-н,)|(\w+\sрн,' \
        r')|(\s№\s)|(\sг,)'

KPI = ('PSS:', 'OSA:', 'TT:', 'VISITS:', 'ISA-OSA:')


async def kpi_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.kpi_menu)
    await UserState.kpi_menu.set()


async def convert_datetime(value: str):
    return dt.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%d %B %Y')


@decorators.error_handler_message
async def kpi_mr(message: types.Message, state: FSMContext):
    query = await db.get_one(
        await queries.get_value(
            value='*',
            table='users'),
        tg_id=int(message.from_user.id))
    up_date = await convert_datetime(query[24])
    await message.answer(
        text=f'```\n'
             f'        план|    факт|результат\n'
             f'{KPI[0]:<4}'
             f'{query[11]:>8.2%}|{query[12]:>8.2%}|{query[13]:>8.2%}\n'
             f'{KPI[1]:<4}'
             f'{query[14]:>8.2%}|{query[15]:>8.2%}|{query[16]:>8.2%}\n'
             f'{KPI[2]:<4}'
             f'{query[17]:>8}|{query[18]:>8}|{query[19]:>8.2%}\n'
             f'{KPI[3]:<7}'
             f'{query[20]:>5}|{query[21]:>8}|{query[22]:>8.2%}\n'
             f'{KPI[4]:<7}{query[23]:>22}'
             f'\n\nАктуальность данных:\n{up_date}```',
        reply_markup=keyboards.back,
        parse_mode='MarkdownV2')


async def kpi_tt(message: types.Message):
    await message.answer(
        text='Введите 7-и значный номер ТТ:',
        reply_markup=keyboards.back)
    await UserState.kpi_search_tt.set()


@decorators.error_handler_message
async def kpi_search_tt(message: types.Message, state: FSMContext):
    tt_num = re.sub(r'\s', '', str(message.text))
    if re.match(r'\d{7}', tt_num) and len(tt_num) == 7:
        query = await db.get_one(
            await queries.get_value(
                value='*',
                table='tt'),
            tt_num=tt_num)
        if query:
            address = re.sub(R_STR, '', query[4])
            address = address \
                .replace("_", "\\_") \
                .replace(".", "\\.") \
                .replace("-", "\\-") \
                .replace("*", "\\*") \
                .replace("@", "\\@") \
                .replace("&", "\\&")
            mr = query[5].replace("_", "\\_")
            up_date = await convert_datetime(query[24])
            await message.answer(
                text=f'*TT №* {tt_num}\n'
                     f'*Сеть:* {query[3]}\n'
                     f'*Адрес:* {address}\n'
                     f'*MR:* {mr}\n'
                     f'*KAS:* {query[6]}\n\n'
                     f'```\n'
                     f'        план|    факт|результат\n'
                     f'{KPI[0]:<4}'
                     f'{query[8]:>8.2%}|{query[9]:>8.2%}|{query[10]:>8.2%}\n'
                     f'{KPI[1]:<4}'
                     f'{query[11]:>8.2%}|{query[12]:>8.2%}|{query[13]:>8.2%}\n'
                     f'{KPI[2]:<4}'
                     f'{query[14]:>8}|{query[15]:>8}|{query[16]:>8.2%}\n'
                     f'{KPI[3]:<7}'
                     f'{query[17]:>5}|{query[18]:>8}|{query[19]:>8.2%}\n'
                     f'{KPI[4]:<7}{query[20]:>22}'
                     f'\n\nАктуальность данных:\n{up_date}```',
                reply_markup=keyboards.back,
                parse_mode='MarkdownV2')
        else:
            await message.answer(
                text='❗ ТТ с таким номером не найдена!\n'
                     'Попробуйте еще раз!',
                reply_markup=keyboards.back)
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
        async with aiofiles.open(file, 'rb') as photo:
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
