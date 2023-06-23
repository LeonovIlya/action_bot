import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from typing import Union

from loader import db
from utils import keyboards, queries
from utils.states import UserState


async def get_auth_level_state(user_tg_id: int) -> Union[UserState,
                                                         ValueError]:
    auth_level = await db.get_one(await queries.get_value(value='position',
                                                          table='users'),
                                  tg_id=user_tg_id)
    if auth_level:
        match auth_level[0]:
            case 'mr':
                return await UserState.auth_mr.set()
            case 'kas':
                return await UserState.auth_kas.set()
            case 'citimanager':
                return await UserState.auth_citimanager.set()
    else:
        raise ValueError


async def start_no_auth(message: types.Message):
    auth = bool(await db.get_one(await queries.get_value(value='tg_id',
                                                         table='users'),
                                 tg_id=int(message.from_user.id)))
    if auth:
        await message.answer(text='Выберите пункт из меню:',
                             reply_markup=keyboards.start_menu_merch)
        await get_auth_level_state(int(message.from_user.id))
    else:
        await message.answer(text='Вас приветствует чат-бот компании '
                                  '"Action"\nДля начала работы с ботом нажмите'
                                  ' /start')


async def start_auth(message: types.Message):
    await message.answer(text='Введите ваш логин:')
    await UserState.start_auth_get_login.set()


async def login_check(message: types.Message, state: FSMContext):
    login = bool(await db.get_one(await queries.get_value(value='ter_num',
                                                          table='users'),
                                  ter_num=str(message.text)))
    if login:
        await state.update_data(ter_num=str(message.text))
        await message.answer(text='Введите ваш пароль:')
        await UserState.start_auth_get_password.set()
    else:
        await message.answer(text='Кажется вы ошиблись, попробуйте еще раз!')


async def password_check(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = bool(await db.get_one(await queries.get_value(value='password',
                                                             table='users'),
                                     ter_num=str(data['ter_num']),
                                     password=str(message.text)))
    if password:
        await db.post(queries.UPDATE_TG_ID,
                      tg_id=int(message.from_user.id),
                      ter_num=str(data['ter_num']))
        username = await db.get_one(await queries.get_value(value='username',
                                                            table='users'),
                                    tg_id=int(message.from_user.id))
        await message.answer(text=f'Добро пожаловать,\n'
                                  f'<b>{username[0]}!</b>\n\n'
                                  f'Выберите пункт из меню:',
                             reply_markup=keyboards.start_menu_merch)
        await get_auth_level_state(int(message.from_user.id))


# стартовое меню бота
async def start_menu_from_button(message: types.Message, state: FSMContext):
    try:
        await get_auth_level_state(int(message.from_user.id))
        await message.answer(text='Выберите пункт из меню:',
                             reply_markup=keyboards.start_menu_merch)
    except ValueError as error:
        await message.answer(text='Кажется вы не авторизованы в боте!\n'
                                  'Нажмите /start для авторизации!')
        await state.finish()
        logging.info(f'Auth error: {error}, user: {int(message.from_user.id)}')


# компануем в обработчик
def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start_auth, commands=['start'])
    dp.register_message_handler(start_no_auth)
    dp.register_message_handler(login_check,
                                state=UserState.start_auth_get_login)
    dp.register_message_handler(password_check,
                                state=UserState.start_auth_get_password)
    dp.register_message_handler(start_menu_from_button,
                                text='Главное меню📱',
                                state='*')
