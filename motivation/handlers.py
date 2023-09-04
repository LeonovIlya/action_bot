import asyncio
import re
from datetime import datetime as dt
import aiofiles
from aiopath import AsyncPath

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import db
from users.handlers import get_value_by_tgig
from utils import decorators, keyboards, queries
from utils.states import UserState


async def mp_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.mp_menu)
    await UserState.mp_menu.set()


@decorators.error_handler_message
async def get_current_mp(message: types.Message, state: FSMContext):
    data = await db.get_all(
        await queries.get_value(
            value='*',
            table='mp'),
        position=await get_value_by_tgig(
            value='position',
            tg_id=int(message.from_user.id)),
        region=await get_value_by_tgig(
            value='region',
            tg_id=int(message.from_user.id)),
        is_active=True,
        is_over=False)
    if data:
        await message.answer(
            text='Мотивационные Программы в вашем регионе:',
            reply_markup=keyboards.back)
        for i in data:
            datetime_start = dt.strptime(i[4], '%Y-%m-%d %H:%M:%S')
            datetime_stop = dt.strptime(i[5], '%Y-%m-%d %H:%M:%S')
            start = datetime_start.strftime('%d %B %Y')
            stop = datetime_stop.strftime('%d %B %Y')
            keyboard = InlineKeyboardMarkup()
            keyboard.insert(
                InlineKeyboardButton('Механика МП',
                                     callback_data=f'mech_file_{i[0]}'))
            keyboard.insert(
                InlineKeyboardButton('Статистика МП',
                                     callback_data=f'stat_file_{i[0]}'))
            await message.answer(
                text=f'<b>{i[1]}</b>\n\n'
                     f'<b>Дата начала:</b> {start}\n'
                     f'<b>Дата окончания:</b> {stop}\n',
                reply_markup=keyboard)
    else:
        await message.answer(
            text='На данный момент нет доступных Мотивационных Программ '
                 'в вашем регионе!',
            reply_markup=keyboards.back)


@decorators.error_handler_message
async def get_archive_mp(message: types.Message, state: FSMContext):
    data = await db.get_all(
        await queries.get_value(
            value='*',
            table='mp'),
        position=await get_value_by_tgig(
            value='position',
            tg_id=int(message.from_user.id)),
        region=await get_value_by_tgig(
            value='region',
            tg_id=int(message.from_user.id)),
        is_active=True,
        is_over=True)
    if data:
        await message.answer(
            text='Архивные Мотивационные Программы в вашем регионе:',
            reply_markup=keyboards.back)
        for i in data:
            datetime_start = dt.strptime(i[4], '%Y-%m-%d %H:%M:%S')
            datetime_stop = dt.strptime(i[5], '%Y-%m-%d %H:%M:%S')
            start = datetime_start.strftime('%d %B %Y')
            stop = datetime_stop.strftime('%d %B %Y')
            keyboard = InlineKeyboardMarkup()
            keyboard.insert(
                InlineKeyboardButton('Механика МП',
                                     callback_data=f'mech_file_{i[0]}'))
            keyboard.insert(
                InlineKeyboardButton('Статистика МП',
                                     callback_data=f'stat_file_{i[0]}'))
            await message.answer(
                text=f'<b>{i[1]}</b>\n\n'
                     f'<b>Дата начала:</b> {start}\n'
                     f'<b>Дата окончания:</b> {stop}\n',
                reply_markup=keyboard
            )
    else:
        await message.answer(
            text='К сожалению в архиве пока пусто(',
            reply_markup=keyboards.back)


@decorators.error_handler_callback
async def send_file_mp(callback: types.CallbackQuery, state: FSMContext):
    mp_id = re.search('\d+', str(callback.data)).group(0)
    call_text = re.sub(r'_\d+', '',  str(callback.data))
    data = await db.get_one(
        await queries.get_value(
            value=call_text,
            table='mp'),
        id=mp_id)
    file = AsyncPath(data[0])
    if await file.is_file():
        await callback.answer(
            text='Отправляю файл...',
            show_alert=False)
        await asyncio.sleep(0.5)
        async with aiofiles.open(file, 'rb') as file:
            await callback.message.answer_chat_action(
                action='upload_document')
            await callback.message.answer_document(
                file,
                reply_markup=keyboards.back)
    else:
        await callback.bot.answer_callback_query(callback.id)
        await callback.message.answer(
            text='Файл не найден!',
            reply_markup=keyboards.back)


def register_handlers_motivation(dp: Dispatcher):
    dp.register_message_handler(
        mp_menu,
        text='Назад↩',
        state=UserState.mp_menu)
    dp.register_message_handler(
        mp_menu,
        text='МП🤩',
        state=(UserState.auth_mr,
               UserState.auth_kas,
               UserState.auth_cm))
    dp.register_message_handler(
        get_current_mp,
        text='Текущие МП💸',
        state=UserState.mp_menu)
    dp.register_message_handler(
        get_archive_mp,
        text='Архив МП🗃',
        state=UserState.mp_menu)
    dp.register_callback_query_handler(
        send_file_mp,
        state=UserState.mp_menu)
