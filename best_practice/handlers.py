import aiofiles
import datetime
import locale
import logging
from aiopath import AsyncPath
from aiofiles import os as aios

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
    try:
        data = await db.get_all(queries.BP_NAME,
                                is_active=True)
        if data:
            await message.answer(text='Практики, доступные на данный момент:',
                                 reply_markup=keyboards.back)
            current_practice = [i for i in data]
            for i in current_practice:
                datetime_start = datetime.datetime.strptime(i[2],
                                                            '%Y-%m-%d %H:%M:%S')
                datetime_stop = datetime.datetime.strptime(i[3],
                                                           '%Y-%m-%d %H:%M:%S')
                start = datetime_start.strftime('%d %B %Y')
                stop = datetime_stop.strftime('%d %B %Y')
                file = AsyncPath(str(i[4]))
                inline_keyboard = InlineKeyboardMarkup()
                inline_keyboard.insert(
                    InlineKeyboardButton('Участвовать!',
                                         callback_data=f'{i[0]}'))
                if await file.is_file():
                    async with aiofiles.open(str(i[4]), 'rb') as file:
                        await message.answer_photo(photo=file,
                                                   caption=f'<b>'
                                                           f'{str(i[0])}</b'
                                                           f'>\n\n '
                                                           f'{str(i[1])}\n\n'
                                                           f'<b>Дата '
                                                           f'начала:</b>\n '
                                                           f'{str(start)}\n\n'
                                                           f'<b>Дата '
                                                           f'окончания:</b>\n '
                                                           f'{str(stop)}',
                                                   reply_markup=inline_keyboard)
                else:
                    await message.answer(text=f'<b>'
                                              f'{str(i[0])}</b>\n\n '
                                              f'{str(i[1])}\n\n'
                                              f'<b>Дата начала:</b>\n '
                                              f'{str(start)}\n\n'
                                              f'<b>Дата окончания:</b>\n '
                                              f'{str(stop)}',
                                         reply_markup=inline_keyboard)
        else:
            await message.answer(
                text='Доступных практик на данный момент нет!',
                reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'DB error: {error}, user: {int(message.from_user.id)}')


async def take_part(callback: types.CallbackQuery, state: FSMContext):
    bp_name = callback.data
    try:
        username = await db.get_one(
            await queries.get_value(
                value='username',
                table='users'),
            tg_id=int(callback.from_user.id))
        check_part = bool(
            await db.get_one(
                await queries.get_value(
                    value='*',
                    table='best_practice_mr'),
                username=str(username[0]),
                best_practice=str(bp_name)))
        if check_part:
            await callback.answer(text='Вы уже участвуете!',
                                  show_alert=False)
        else:
            confirm_keyboard = InlineKeyboardMarkup()
            confirm_keyboard.insert(
                InlineKeyboardButton('Да',
                                     callback_data='bp_yes'))
            confirm_keyboard.insert(
                InlineKeyboardButton('Нет',
                                     callback_data='bp_no'))
            await state.update_data(bp_name=str(bp_name))
            await callback.message.answer(text=f'Вы уверены, что хотите '
                                               f'участвовать в практике:\n'
                                               f'<b>{bp_name}?</b>',
                                          reply_markup=confirm_keyboard)
            await UserState.practice_take_part_mr_confirm.set()
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'DB error: {error}, user: {int(message.from_user.id)}')


async def take_part_confirmation(callback: types.CallbackQuery):
    await callback.bot.answer_callback_query(callback.id)
    if callback.data == 'bp_yes':
        await callback.message.answer(text='Отправьте фотографию:')
        await UserState.practice_take_part_mr_send.set()
    if callback.data == 'bp_no':
        await callback.message.delete()
        await UserState.practice_menu_mr.set()


async def take_part_take_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    bp_name = data['bp_name']
    tg_id = message.from_user.id
    try:
        bp_id = await db.get_one(
            await queries.get_value(
                value='id',
                table='best_practice'),
            name=bp_name)
        destination = f'./files/best_practice/{int(bp_id[0])}/{int(tg_id)}.jpg'
        await message.photo[-1].download(destination_file=destination,
                                         make_dirs=True)
        username = await db.get_one(
            await queries.get_value(
                value='username',
                table='users'),
            tg_id=int(message.from_user.id))
        await db.post(queries.INSERT_PRACTICE_MR,
                      best_practice=str(bp_name),
                      username=str(username[0]),
                      datetime_added=datetime.datetime.now(),
                      pics=str(destination))
        await message.answer(text='Ваше заявка принята, ожидайте решения!',
                             reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'DB error: {error}, user: {int(message.from_user.id)}')


async def make_suggest(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


async def add_new_practice_add_name(message: types.Message):
    await message.answer(text='Напишите название новой практики:',
                         reply_markup=keyboards.back)
    await UserState.practice_add.set()


async def add_new_practice_add_desc(message: types.Message, state: FSMContext):
    await state.update_data(name=str(message.text))
    await message.answer(text='Добавьте описание для новой практики:',
                         reply_markup=keyboards.back)
    await UserState.practice_add_desc.set()


async def add_new_practice_add_start(message: types.Message,
                                     state: FSMContext):
    await state.update_data(desc=str(message.text))
    await message.answer(text='Введите дату начала в формате "20-01-2003":',
                         reply_markup=keyboards.back)
    await UserState.practice_add_start.set()


async def add_new_practice_add_stop(message: types.Message, state: FSMContext):
    try:
        date_start = datetime.datetime.strptime(str(message.text), '%d-%m-%Y')
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
        date_stop = datetime.datetime.strptime(str(message.text), '%d-%m-%Y')
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
    try:
        max_id = await db.get_one(queries.MAX_ID)
        if max_id[0] is None:
            max_id = ('0',)
        data = await state.get_data()
        user_id = await db.get_one(
            await queries.get_value(
                value='id',
                table='users'),
            tg_id=int(message.from_user.id))
        destination = f'./files/best_practice/{int(max_id[0]) + 1}/1.jpg'
        await message.photo[-1].download(destination_file=destination,
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
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'DB error: {error}, user: {int(message.from_user.id)}')


async def manage_practice(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


def register_handlers_best_practice(dp: Dispatcher):
    dp.register_message_handler(practice_menu_mr,
                                text='Назад↩',
                                state=(UserState.practice_menu_mr,
                                       UserState.practice_menu_kas,
                                       UserState.practice_menu_citimanager,
                                       UserState.practice_take_part_mr_send,
                                       UserState.practice_add_picture))

    dp.register_message_handler(practice_menu_mr,
                                text='Практики🗣',
                                state=UserState.auth_mr)
    dp.register_message_handler(practice_menu_citimanager,
                                text='Практики🗣',
                                state=UserState.auth_citimanager)
    dp.register_message_handler(get_current_practice,
                                text='Текущие практики🎯',
                                state=UserState.practice_menu_mr)
    dp.register_message_handler(make_suggest,
                                text='Предложения📝',
                                state=UserState.practice_menu_mr)

    dp.register_callback_query_handler(take_part,
                                       state=UserState.practice_menu_mr)
    dp.register_callback_query_handler(take_part_confirmation,
                                       state=UserState.practice_take_part_mr_confirm)
    dp.register_message_handler(take_part_take_photo,
                                content_types=['photo'],
                                state=UserState.practice_take_part_mr_send)

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
