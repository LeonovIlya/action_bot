import hashlib
import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from typing import Union

from loader import db
from utils import keyboards, queries
from utils.states import UserState


async def start_menu_and_state(message: types.Message, state: FSMContext):
    try:
        position = await db.get_one(
            await queries.get_value(
                value='position',
                table='users'),
            tg_id=int(message.from_user.id))
        await state.reset_state()
        await state.reset_data()
        if position:
            match position[0]:
                case 'mr':
                    await message.answer(text='Выберите пункт из меню:',
                                         reply_markup=keyboards.start_menu_mr)
                    await UserState.auth_mr.set()
                case 'kas':
                    await message.answer(text='Выберите пункт из меню:',
                                         reply_markup=keyboards.start_menu_kas)
                    await UserState.auth_kas.set()
                case 'cm':
                    await message.answer(text='Выберите пункт из меню:',
                                         reply_markup=keyboards.start_menu_cm)
                    await UserState.auth_cm.set()
        else:
            await message.answer(text='Вас приветствует чат-бот компании '
                                      '"Action"\nДля начала работы с ботом '
                                      'нажмите кнопку "START"',
                                 reply_markup=keyboards.start)
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def start_no_auth(message: types.Message, state: FSMContext):
    try:
        auth = bool(await db.get_one(
            await queries.get_value(
                value='tg_id',
                table='users'),
            tg_id=int(message.from_user.id)))
        if auth:
            await start_menu_and_state(message, state)
        else:
            await message.answer(text='Вас приветствует чат-бот компании '
                                      '"Action"\nДля начала работы с ботом '
                                      'нажмите кнопку "START"',
                                 reply_markup=keyboards.start)
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def start_auth(message: types.Message):
    await message.answer(text='Введите ваш логин:')
    await UserState.start_auth_get_login.set()


async def login_check(message: types.Message, state: FSMContext):
    try:
        login = bool(await db.get_one(
            await queries.get_value(
                value='ter_num',
                table='users'),
            ter_num=str(message.text)))
        if login:
            await state.update_data(ter_num=str(message.text))
            await message.answer(text='Введите ваш пароль:')
            await UserState.start_auth_get_password.set()
        else:
            await message.answer(text='Кажется вы ошиблись, попробуйте еще '
                                      'раз!')
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def password_check(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        pwd_hash = hashlib.sha512(str(message.text).encode(
            'utf-8')).hexdigest()
        check_password = bool(await db.get_one(
            await queries.get_value(
                value='password',
                table='users'),
            ter_num=str(data['ter_num']),
            password=pwd_hash))
        if check_password:
            await db.post(queries.UPDATE_TG_ID,
                          tg_id=int(message.from_user.id),
                          ter_num=str(data['ter_num']))
            await message.answer(text='Добро пожаловать!')
            await start_menu_and_state(message, state)
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def logout(message: types.Message, state: FSMContext):
    try:
        await db.post(queries.LOGOUT,
                      tg_id=message.from_user.id)
        await message.answer(text='Вы успешно разлогинились!')
        await state.reset_data()
        await state.finish()
    except Exception as error:
        await message.answer(text='Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


# компануем в обработчик
def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start_auth,
                                text='START▶️')
    dp.register_message_handler(start_no_auth)
    dp.register_message_handler(login_check,
                                state=UserState.start_auth_get_login)
    dp.register_message_handler(password_check,
                                state=UserState.start_auth_get_password)
    dp.register_message_handler(start_menu_and_state,
                                text='Главное меню📱',
                                state='*')
    dp.register_message_handler(logout,
                                commands=['logout'],
                                state='*')
