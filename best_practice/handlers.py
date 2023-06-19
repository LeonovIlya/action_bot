import aiofiles
import datetime
import logging
from aiopath import AsyncPath
from aiofiles import os as aios

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState


async def practice_menu_mr(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.practice_menu_merch)
    await UserState.practice_menu_mr.set()


async def practice_menu_citimanager(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.practice_menu_citimanager)
    await UserState.practice_menu_citimanager.set()


async def get_current_practice(message: types.Message):
    current_practice = await db.get_stuff_list(queries.BP_NAME,
                                               is_active=True)
    print(current_practice)
    for i in current_practice:
        file = AsyncPath(i[4])
        if await file.is_file():
            async with aiofiles.open(i[4], 'rb') as file:
                await message.answer_photo(photo=file,
                                           caption=f'<b>'
                                                   f'{i[0]}</b>\n\n'
                                                   f'{i[1]}\n\n'
                                                   f'Дата начала: '
                                                   f'{i[2]}\n'
                                                   f'Дата окончания: '
                                                   f'{i[3]}')
        else:
            await message.answer(text='Файл не найден!',
                                 reply_markup=keyboards.back)


async def add_new_practice_add_name(message: types.Message):
    await message.answer(text='Напишите название новой практики:')
    await UserState.practice_add.set()


async def add_new_practice_add_desc(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Добавьте описание для новой практики:')
    await UserState.practice_add_desc.set()


async def add_new_practice_add_picture(message: types.Message,
                                       state: FSMContext):
    await state.update_data(desc=message.text)
    await message.answer(text='Добавьте фотографию для новой практики:')
    await UserState.practice_add_picture.set()


async def add_new_practice(message: types.Message, state: FSMContext):
    max_id = await db.get_one(queries.MAX_ID)
    data = await state.get_data()
    user_id = await db.get_one(await queries.get_value_by_tg_id('id'),
                               tg_id=message.from_user.id)
    # await aios.makedirs(f'./files/best_practice/{max_id + 1}',
    #                     exist_ok=True)
    destination = f'./files/best_practice/{max_id + 1}/1.jpg'
    await message.photo[-1].download(destination=destination,
                                     make_dirs=True)
    await db.post(queries.INSERT_PRACTICE,
                  name=data['name'],
                  desc=data['desc'],
                  user_added=user_id,
                  datetime_added=datetime.datetime.now(),
                  is_active=True,
                  pics=destination)
    await message.answer(text='Успешно добавлено',
                         reply_markup=keyboards.back)
    await state.finish()


def register_handlers_best_practice(dp: Dispatcher):
    dp.register_message_handler(practice_menu_mr,
                                text='Практики🗣',
                                state=UserState.auth_mr)
    dp.register_message_handler(practice_menu_citimanager,
                                text='Практики🗣',
                                state=UserState.auth_citimanager)
    dp.register_message_handler(get_current_practice,
                                text='Текущие практики🎯',
                                state=UserState.practice_menu_mr)
    dp.register_message_handler(add_new_practice_add_name,
                                text='Добавить новую',
                                state=UserState.practice_menu_citimanager)
    dp.register_message_handler(add_new_practice_add_desc,
                                state=UserState.practice_add)
    dp.register_message_handler(add_new_practice_add_picture,
                                state=UserState.practice_add_desc)
    dp.register_message_handler(add_new_practice,
                                content_types=['photo'],
                                state=UserState.practice_add_picture)
