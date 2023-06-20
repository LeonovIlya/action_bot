import aiofiles
import datetime
import locale
import logging
from aiopath import AsyncPath
from aiofiles import os as aios

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


async def practice_menu_mr(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.practice_menu_merch)
    await UserState.practice_menu_mr.set()


async def practice_menu_citimanager(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.practice_menu_citimanager)
    await UserState.practice_menu_citimanager.set()


async def get_current_practice(message: types.Message):
    current_practice = await db.get_list(queries.BP_NAME,
                                         is_active=True)
    for i in current_practice:
        datetime_start = datetime.datetime.strptime(str(i[2]),
                                                    '%Y-%m-%d %H:%M:%S')
        datetime_stop = datetime.datetime.strptime(str(i[3]),
                                                   '%Y-%m-%d %H:%M:%S')
        start = datetime_start.strftime('%d %B %Y')
        stop = datetime_stop.strftime('%d %B %Y')
        file = AsyncPath(str(i[4]))
        if await file.is_file():
            async with aiofiles.open(str(i[4]), 'rb') as file:
                await message.answer_photo(photo=file,
                                           caption=f'<b>'
                                                   f'{str(i[0])}</b>\n\n'
                                                   f'{str(i[1])}\n\n'
                                                   f'<b>Дата начала:</b>\n'
                                                   f'{start}\n\n'
                                                   f'<b>Дата окончания:</b>\n'
                                                   f'{stop}',
                                           reply_markup=keyboards.back)
        else:
            await message.answer(text='Файл не найден!',
                                 reply_markup=keyboards.back)


async def take_part(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


async def make_suggest(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


async def add_new_practice_add_name(message: types.Message):
    await message.answer(text='Напишите название новой практики:',
                         reply_markup=keyboards.back)
    await UserState.practice_add.set()


async def add_new_practice_add_desc(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Добавьте описание для новой практики:',
                         reply_markup=keyboards.back)
    await UserState.practice_add_desc.set()


async def add_new_practice_add_start(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer(text='Введите дату начала в формате "20-01-2003":',
                         reply_markup=keyboards.back)
    await UserState.practice_add_start.set()


async def add_new_practice_add_stop(message: types.Message, state: FSMContext):
    try:
        date_start = datetime.datetime.strptime(message.text, '%d-%m-%Y')
        if date_start < datetime.datetime.now():
            await message.answer(text='Дата начала должна быть позднее '
                                      'текущей даты!\nВведите дату еще раз!')
        else:
            await state.update_data(date_start=date_start)
            await message.answer(text='Введите дату окончания в формате '
                                      '"20-01-2003":',
                                 reply_markup=keyboards.back)
            await UserState.practice_add_stop.set()
    except ValueError:
        await message.answer(text='Неверный ввод, попробуйте еще раз!')


async def add_new_practice_add_picture(message: types.Message,
                                       state: FSMContext):
    try:
        date_stop = datetime.datetime.strptime(message.text, '%d-%m-%Y')
        if date_stop < datetime.datetime.now():
            await message.answer(text='Дата окончания должна быть позднее '
                                      'текущей даты!\nВведите дату еще раз!')
        else:
            data = await state.get_data()
            if date_stop < data['date_start']:
                await message.answer(text='Дата окончания должна быть '
                                          'позднее даты начала!\nВведите '
                                          'дату еще раз!')
            else:
                await state.update_data(date_stop=date_stop)
                await message.answer(text='Добавьте фотографию для новой '
                                          'практики:',
                                     reply_markup=keyboards.back)
                await UserState.practice_add_picture.set()
    except ValueError:
        await message.answer(text='Неверный ввод, попробуйте еще раз!')


async def add_new_practice(message: types.Message, state: FSMContext):
    max_id = await db.get_one(queries.MAX_ID)
    if max_id[0] is None:
        max_id = ('0',)
    data = await state.get_data()
    user_id = await db.get_one(await queries.get_value('id'),
                               tg_id=message.from_user.id)
    destination = f'./files/best_practice/{int(max_id[0]) + 1}/1.jpg'
    await message.photo[-1].download(destination=destination,
                                     make_dirs=True)
    await db.post(queries.INSERT_PRACTICE,
                  name=data['name'],
                  desc=data['desc'],
                  user_added=user_id[0],
                  datetime_added=datetime.datetime.now(),
                  datetime_start=data['date_start'],
                  datetime_stop=data['date_stop'],
                  is_active=True,
                  pics=destination)
    await message.answer(text='Успешно добавлено',
                         reply_markup=keyboards.back)


async def manage_practice(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


def register_handlers_best_practice(dp: Dispatcher):
    dp.register_message_handler(practice_menu_mr,
                                text='Назад↩',
                                state=UserState.practice_menu_mr)
    dp.register_message_handler(practice_menu_mr,
                                text='Назад↩',
                                state=UserState.practice_menu_citimanager)
    dp.register_message_handler(practice_menu_mr,
                                text='Практики🗣',
                                state=UserState.auth_mr)
    dp.register_message_handler(practice_menu_citimanager,
                                text='Практики🗣',
                                state=UserState.auth_citimanager)
    dp.register_message_handler(get_current_practice,
                                text='Текущие практики🎯',
                                state=UserState.practice_menu_mr)
    dp.register_message_handler(take_part,
                                text='Участвовать📸',
                                state=UserState.practice_menu_mr)
    dp.register_message_handler(make_suggest,
                                text='Предложения📝',
                                state=UserState.practice_menu_mr)
    dp.register_message_handler(add_new_practice_add_name,
                                text='Добавить новую➕',
                                state=UserState.practice_menu_citimanager)
    dp.register_message_handler(add_new_practice_add_desc,
                                state=UserState.practice_add)
    dp.register_message_handler(add_new_practice_add_start,
                                state=UserState.practice_add_desc)
    dp.register_message_handler(add_new_practice_add_stop,
                                state=UserState.practice_add_start)
    dp.register_message_handler(add_new_practice_add_picture,
                                state=UserState.practice_add_stop)
    dp.register_message_handler(add_new_practice,
                                content_types=['photo'],
                                state=UserState.practice_add_picture)
    dp.register_message_handler(manage_practice,
                                text='Управлять текущими🔀',
                                state=UserState.practice_menu_citimanager)
