import aiofiles
import asyncio
import datetime
import locale
import logging
from aiopath import AsyncPath

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from loader import db
from utils import keyboards, queries
from utils.states import UserState

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


async def practice_menu_mr(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.practice_menu_mr)
    await UserState.practice_menu_mr.set()


async def practice_menu_kas(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.practice_menu_kas)
    await UserState.practice_menu_kas.set()


async def practice_menu_cm(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.practice_menu_cm)
    await UserState.practice_menu_cm.set()


async def manage_practice(message: types.Message):
    try:
        region = await db.get_one(
            await queries.get_value(
                value='region',
                table='users'
            ),
            tg_id=int(message.from_user.id)
        )
        data = await db.get_all(queries.BP_NAME,
                                region=region[0],
                                over=False)
        if data:
            await message.answer(text='Выберите практику для управления:',
                                 reply_markup=keyboards.back)
            for i in data:
                datetime_start = datetime.datetime.strptime(i[2],
                                                            '%Y-%m-%d %H:%M:%S')
                datetime_stop = datetime.datetime.strptime(i[3],
                                                           '%Y-%m-%d %H:%M:%S')
                start = datetime_start.strftime('%d %B %Y')
                stop = datetime_stop.strftime('%d %B %Y')
                keyboard = InlineKeyboardMarkup()
                keyboard.insert(
                    InlineKeyboardButton('Управлять',
                                         callback_data=f'{i[0]}'))
                file = AsyncPath(str(i[4]))
                if await file.is_file():
                    async with aiofiles.open(str(i[4]), 'rb') as photo:
                        await message.answer_photo(photo=photo,
                                                   caption=f'<b>'
                                                           f'{str(i[0])}</b'
                                                           f'>\n\n'
                                                           f'{str(i[1])}\n\n'
                                                           f'<b>Дата '
                                                           f'начала:</b>\n'
                                                           f'{str(start)}\n\n'
                                                           f'<b>Дата '
                                                           f'окончания:</b>\n'
                                                           f'{str(stop)}',
                                                   reply_markup=keyboard)
                else:
                    await message.answer(text=f'<b>'
                                              f'{str(i[0])}</b>\n\n '
                                              f'{str(i[1])}\n\n'
                                              f'<b>Дата начала:</b>\n '
                                              f'{str(start)}\n\n'
                                              f'<b>Дата окончания:</b>\n '
                                              f'{str(stop)}',
                                         reply_markup=keyboard)
                await UserState.practice_manage_cm.set()
        else:
            await message.answer(
                text='Нет практик для управления!',
                reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def select_action_manage(callback: types.CallbackQuery,
                               state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    await state.update_data(bp_name=str(callback.data))
    # await callback.message.answer(text=f'<b><u>{str(callback.data)}</u></b>',
    #                               reply_markup=keyboards.manage_keyboard)
    await callback.message.edit_reply_markup(
        reply_markup=keyboards.manage_keyboard)
    await UserState.practice_manage_action_cm.set()


async def action_manage(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    data = await state.get_data()
    match callback.data:
        case 'change_name':
            await callback.message.delete()
            await callback.message.answer(text='Введите новое название для '
                                               'практики:\n'
                                               '(Не более 45 символов, '
                                               'вместе с пробелами!)')
            await UserState.practice_manage_change_name.set()

        case 'change_desc':
            await callback.message.delete()
            await callback.message.answer(text='Введите новое описание для '
                                               'практики:')
            await UserState.practice_manage_change_desc.set()
        case 'change_pic':
            await callback.message.delete()
            await callback.message.answer(text='Отправьте новую фотографию:')
            await UserState.practice_manage_change_pic.set()
        case 'change_start':
            await callback.message.delete()
            await callback.message.answer(text='Введите новую дату начала в '
                                               'формате "20-01-2003":')
            await UserState.practice_manage_change_start.set()
        case 'change_stop':
            await callback.message.delete()
            await callback.message.answer(text='Введите новую дату окончания в'
                                               ' формате "20-01-2003":')
            await UserState.practice_manage_change_stop.set()
        case 'delete_bp':
            await callback.message.answer(text=f'Вы действительно хотите '
                                               f'удалить практику '
                                               f'{data["bp_name"]}',
                                          reply_markup=keyboards.confirm_keyboard)
        case 'bp_yes':
            try:
                await db.post(queries.DELETE_BP, name=data['bp_name'])
                await callback.message.delete()
                await callback.message.answer(text='Практика успешно '
                                                   'удалена!',
                                              reply_markup=keyboards.back)
            except Exception as error:
                await callback.message.answer(text='❗ Кажется что-то пошло '
                                                   'не так!\n'
                                                   'Попробуйте еще раз!')
                logging.info(
                    f'Error: {error}, user: {int(callback.from_user.id)}')
        case 'bp_no':
            await callback.message.delete()


async def manage_change_name(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        name = str(message.text)
        if len(name) > 45:
            await message.answer(text='❗ Превышен лимит в 45 символов!')
        else:
            check_name = bool(await db.get_one(
                await queries.get_value(
                    value='name',
                    table='best_practice'
                ),
                name=name
            ))
            if check_name:
                await message.answer(text='❗ Практика с таким названием уже '
                                          'существует!\n'
                                          'Введите другое название!')
            else:
                await db.post(
                    await queries.change_bp(value='name'),
                    new_name=name,
                    old_name=data['bp_name']
                )
                await message.answer(text='Название успешно изменено!')
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def manage_change_desc(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await db.post(
            await queries.change_bp(value='desc'),
            desc=str(message.text),
            name=data['bp_name']
        )
        await message.answer(text='Описание успешно изменено!')
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def manage_change_pic(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        destination = await db.get_one(
            await queries.get_value(
                value='file_link',
                table='best_practice'
            ),
            name=data['bp_name'])
        await message.photo[-1].download(destination_file=destination[0],
                                         make_dirs=True)
        await message.answer(text='Фотография успешно изменена!')
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def manage_change_start(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        date_start = datetime.datetime.strptime(str(message.text), '%d-%m-%Y')
        if date_start < datetime.datetime.now():
            await message.answer(text='❗ Дата начала должна быть позднее '
                                      'текущей даты!\nВведите дату еще раз!')
        else:
            await db.post(
                await queries.change_bp(value='datetime_start'),
                datetime_start=date_start,
                name=data['bp_name'])
            await message.answer(text='Дата начала успешно изменена!')
    except ValueError:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def manage_change_stop(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        date_stop = datetime.datetime.strptime(str(message.text), '%d-%m-%Y')
        if date_stop < datetime.datetime.now():
            await message.answer(text='❗ Дата окончания должна быть позднее '
                                      'текущей даты!\nВведите дату еще раз!')
        else:
            date_start = await db.get_one(
                await queries.get_value(
                    value='datetime_start',
                    table='best_practice'
                ),
                name=data['bp_name']
            )
            date_start = datetime.datetime.strptime(date_start[0],
                                                    '%Y-%m-%d %H:%M:%S')
            if date_stop < date_start:
                await message.answer(text='❗ Дата окончания должна быть '
                                          'позднее даты начала!\nВведите '
                                          'дату еще раз!')
            else:
                await db.post(
                    await queries.change_bp(value='datetime_stop'),
                    datetime_stop=date_stop,
                    name=data['bp_name'])
                await message.answer(text='Дата окончания успешно изменена!')
    except ValueError:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def get_current_practice(message: types.Message):
    try:
        region = await db.get_one(
            await queries.get_value(
                value='region',
                table='users'
            ),
            tg_id=int(message.from_user.id)
        )
        data = await db.get_all(queries.BP_NAME,
                                region=region[0],
                                is_active=True,
                                over=False)
        if data:
            await message.answer(text='Практики, доступные на данный момент:',
                                 reply_markup=keyboards.back)
            for i in data:
                datetime_start = datetime.datetime.strptime(i[2],
                                                            '%Y-%m-%d %H:%M:%S')
                datetime_stop = datetime.datetime.strptime(i[3],
                                                           '%Y-%m-%d %H:%M:%S')
                start = datetime_start.strftime('%d %B %Y')
                stop = datetime_stop.strftime('%d %B %Y')
                file = AsyncPath(str(i[4]))
                inline_keyboard = InlineKeyboardMarkup()
                inline_keyboard.insert(
                    InlineKeyboardButton('Участвовать!📨',
                                         callback_data=f'{i[0]}'))
                if await file.is_file():
                    async with aiofiles.open(str(i[4]), 'rb') as file:
                        await message.answer_photo(photo=file,
                                                   caption=f'<b>'
                                                           f'{str(i[0])}</b'
                                                           f'>\n\n'
                                                           f'{str(i[1])}\n\n'
                                                           f'<b>Дата '
                                                           f'начала:</b>\n'
                                                           f'{str(start)}\n\n'
                                                           f'<b>Дата '
                                                           f'окончания:</b>\n'
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
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def take_part(callback: types.CallbackQuery, state: FSMContext):
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
                best_practice=str(callback.data)))
        if check_part:
            await callback.answer(text='Вы уже участвуете!',
                                  show_alert=False)
        else:
            await state.update_data(bp_name=str(callback.data))
            await state.update_data(username=str(username[0]))
            await callback.message.answer(text=f'Вы уверены, что хотите '
                                               f'участвовать в практике:\n'
                                               f'<b>{callback.data}?</b>',
                                          reply_markup=keyboards.confirm_keyboard)
            await UserState.practice_take_part_mr_confirm.set()
    except Exception as error:
        await callback.message.answer(text='❗ Кажется что-то пошло не так!\n'
                                           'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(callback.from_user.id)}')


async def take_part_confirmation(callback: types.CallbackQuery):
    await callback.bot.answer_callback_query(callback.id)
    match callback.data:
        case 'bp_yes':
            await callback.message.answer(text='Отправьте фотографию для '
                                               'участия:')
            await UserState.practice_take_part_mr_photo.set()
        case 'bp_no':
            await callback.message.delete()
            await UserState.practice_menu_mr.set()


async def take_part_take_photo(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        bp_id = await db.get_one(
            await queries.get_value(
                value='id',
                table='best_practice'),
            name=str(data['bp_name']))
        destination = f'./files/best_practice/{int(bp_id[0])}/' \
                      f'{int(message.from_user.id)}.jpg '
        await state.update_data(destination=destination)
        await message.photo[-1].download(destination_file=destination,
                                         make_dirs=True)
        await message.answer(text='Добавьте комментарий к фото',
                             reply_markup=keyboards.back)
        await UserState.practice_take_part_mr_desc.set()
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def take_part_take_description(message: types.Message,
                                     state: FSMContext):
    try:
        data = await state.get_data()
        await db.post(queries.INSERT_PRACTICE_MR,
                      best_practice=str(data['bp_name']),
                      username=str(data['username']),
                      tg_id=int(message.from_user.id),
                      datetime_added=datetime.datetime.now(),
                      desc=str(message.text),
                      file_link=str(data['destination']),
                      kas_checked=False,
                      kas_approved=False,
                      cm_checked=False,
                      cm_approved=False,
                      active=False)
        await message.answer(text='Ваше заявка принята, ожидайте решения!',
                             reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def add_new_practice_add_name(message: types.Message):
    await message.answer(text='Введите уникальное название новой практики:\n'
                              '(Не более 45 символов, вместе с пробелами!)',
                         reply_markup=keyboards.back)
    await UserState.practice_add.set()


async def add_new_practice_add_desc(message: types.Message, state: FSMContext):
    try:
        name = str(message.text)
        if len(name) > 45:
            await message.answer(text='❗ Превышен лимит в 45 символов!')
        else:
            check_name = bool(await db.get_one(
                await queries.get_value(
                    value='name',
                    table='best_practice'
                ),
                name=name
            ))
            if check_name:
                await message.answer(text='❗ Практика с таким названием уже '
                                          'существует!\n'
                                          'Введите другое название!')
            else:
                await state.update_data(name=name)
                await message.answer(text='Добавьте описание для новой '
                                          'практики:',
                                     reply_markup=keyboards.back)
                await UserState.practice_add_desc.set()
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


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
            await message.answer(text='❗ Дата начала должна быть позднее '
                                      'текущей даты!\nВведите дату еще раз!')
        else:
            await state.update_data(date_start=date_start)
            await message.answer(text='Введите дату окончания в формате '
                                      '"20-01-2003":',
                                 reply_markup=keyboards.back)
            await UserState.practice_add_stop.set()
    except ValueError:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')


async def add_new_practice_add_picture(message: types.Message,
                                       state: FSMContext):
    try:
        date_stop = datetime.datetime.strptime(str(message.text), '%d-%m-%Y')
        if date_stop < datetime.datetime.now():
            await message.answer(text='❗ Дата окончания должна быть позднее '
                                      'текущей даты!\nВведите дату еще раз!')
        else:
            data = await state.get_data()
            if date_stop < data['date_start']:
                await message.answer(text='❗ Дата окончания должна быть '
                                          'позднее даты начала!\nВведите '
                                          'дату еще раз!')
            else:
                await state.update_data(date_stop=date_stop)
                await message.answer(text='Добавьте фотографию для новой '
                                          'практики:',
                                     reply_markup=keyboards.back)
                await UserState.practice_add_picture.set()
    except ValueError:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')


async def add_new_practice(message: types.Message, state: FSMContext):
    try:
        region = await db.get_one(
            await queries.get_value(
                value='region',
                table='users'
            ),
            tg_id=int(message.from_user.id)
        )
        max_id = await db.get_one(queries.MAX_ID)
        if max_id[0] is None:
            max_id = ('0',)
        data = await state.get_data()
        username = await db.get_one(
            await queries.get_value(
                value='username',
                table='users'),
            tg_id=int(message.from_user.id))
        destination = f'./files/best_practice/{int(max_id[0]) + 1}/1.jpg'
        await message.photo[-1].download(destination_file=destination,
                                         make_dirs=True)
        await db.post(queries.INSERT_PRACTICE,
                      region=region[0],
                      name=data['name'],
                      desc=data['desc'],
                      user_added=username[0],
                      datetime_added=datetime.datetime.now(),
                      datetime_start=data['date_start'],
                      datetime_stop=data['date_stop'],
                      is_active=True,
                      over=False,
                      file_link=destination)
        await message.answer(text='Успешно добавлено',
                             reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def practice_requests_kas(message: types.Message):
    try:
        region = await db.get_one(
            await queries.get_value(
                value='region',
                table='users'
            ),
            tg_id=int(message.from_user.id)
        )
        data = await db.get_all(queries.BP_NAME,
                                region=region[0],
                                is_active=True,
                                over=False)
        if data:
            await message.answer(text='Практики, доступные на данный момент:',
                                 reply_markup=keyboards.back)
            for i in data:
                inline_keyboard = InlineKeyboardMarkup()
                inline_keyboard.insert(
                    InlineKeyboardButton('Смотреть заявки👀',
                                         callback_data=f'{i[0]}'))
                await message.answer(text=f'<b>{i[0]}</b>',
                                     reply_markup=inline_keyboard)
                await UserState.practice_requests_show_kas.set()
        else:
            await message.answer(
                text='Доступных практик на данный момент нет!',
                reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def practice_requests_show_kas(callback: types.CallbackQuery,
                                     state: FSMContext):
    try:
        data = await state.get_data()
        match callback.data:
            case 'Accept':
                await callback.bot.answer_callback_query(callback.id)
                await db.post(queries.BP_KAS,
                              kas_checked=True,
                              kas_approved=True,
                              id=data['bp_id'])
                await callback.bot.send_message(chat_id=data['mr_tg_id'],
                                                text='✅ Ваша заявка на '
                                                     'участие в Лучшей '
                                                     'Практике принята '
                                                     'Супервайзером!')
            case 'Decline':
                await callback.bot.answer_callback_query(callback.id)
                await db.post(queries.BP_KAS,
                              kas_checked=True,
                              kas_approved=False,
                              id=data['bp_id'])
                await callback.bot.send_message(chat_id=data['mr_tg_id'],
                                                text='❗ Ваша заявка на '
                                                     'участие в Лучшей '
                                                     'Практике '
                                                     'отклонена '
                                                     'Супервайзером!')
            case _:
                photo = await db.get_one(queries.BP_PHOTOS,
                                         best_practice=str(callback.data),
                                         kas_checked=False,
                                         kas_approved=False,
                                         cm_checked=False,
                                         cm_approved=False,
                                         active=False)
                if photo:
                    await callback.bot.answer_callback_query(callback.id)
                    await state.update_data(bp_id=photo[0])
                    await state.update_data(mr_tg_id=photo[2])

                    keyboard = InlineKeyboardMarkup()
                    keyboard.insert(
                        InlineKeyboardButton('Принять✅',
                                             callback_data='Accept'))
                    keyboard.insert(
                        InlineKeyboardButton('Отклонить❌',
                                             callback_data='Decline'))
                    keyboard.insert(
                        InlineKeyboardButton('Дальше➡',
                                             callback_data=str(callback.data)))
                    file = AsyncPath(str(photo[4]))
                    if await file.is_file():
                        async with aiofiles.open(str(photo[4]), 'rb') as file:
                            await callback.message.answer_photo(photo=file,
                                                                caption=photo[3],
                                                                reply_markup=keyboard)
                else:
                    await callback.answer(text='Нет заявок для модерации!',
                                          show_alert=True)
                    await callback.message.delete()
    except Exception as error:
        await callback.message.answer(
            text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!')
        logging.info(
            f'Error: {error}, user: {int(callback.from_user.id)}')


async def practice_requests_cm(message: types.Message):
    try:
        region = await db.get_one(
            await queries.get_value(
                value='region',
                table='users'
            ),
            tg_id=int(message.from_user.id)
        )
        data = await db.get_all(queries.BP_NAME,
                                region=region[0],
                                is_active=True,
                                over=False)
        if data:
            await message.answer(text='Практики, доступные на данный момент:',
                                 reply_markup=keyboards.back)
            for i in data:
                inline_keyboard = InlineKeyboardMarkup()
                inline_keyboard.insert(
                    InlineKeyboardButton('Смотреть заявки👀',
                                         callback_data=f'{i[0]}'))
                await message.answer(text=f'<b>{i[0]}</b>',
                                     reply_markup=inline_keyboard)
                await UserState.practice_requests_show_cm.set()
        else:
            await message.answer(
                text='Доступных практик на данный момент нет!',
                reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def practice_requests_show_cm(callback: types.CallbackQuery,
                                    state: FSMContext):
    try:
        data = await state.get_data()
        match callback.data:
            case 'Accept':
                await callback.bot.answer_callback_query(callback.id)
                await db.post(queries.BP_CM,
                              cm_checked=True,
                              cm_approved=True,
                              active=True,
                              id=data['bp_id'])
                await callback.bot.send_message(chat_id=data['mr_tg_id'],
                                                text='✅ Ваша заявка на '
                                                     'участие в Лучшей '
                                                     'Практике принята '
                                                     'СитиМенеджером!')
            case 'Decline':
                await callback.bot.answer_callback_query(callback.id)
                await db.post(queries.BP_CM,
                              cm_checked=True,
                              cm_approved=False,
                              id=data['bp_id'])
                await callback.bot.send_message(chat_id=data['mr_tg_id'],
                                                text='❗ Ваша заявка на '
                                                     'участие в '
                                                     'Лучшей Практике '
                                                     'отклонена '
                                                     'СитиМенеджером!')
            case _:
                photo = await db.get_one(queries.BP_PHOTOS,
                                         best_practice=str(callback.data),
                                         kas_checked=True,
                                         kas_approved=True,
                                         cm_checked=False,
                                         cm_approved=False,
                                         active=False)
                if photo:
                    await callback.bot.answer_callback_query(callback.id)
                    await state.update_data(bp_id=photo[0])
                    await state.update_data(mr_tg_id=photo[2])

                    keyboard = InlineKeyboardMarkup()
                    keyboard.insert(
                        InlineKeyboardButton('Принять✅',
                                             callback_data='Accept'))
                    keyboard.insert(
                        InlineKeyboardButton('Отклонить❌',
                                             callback_data='Decline'))
                    keyboard.insert(
                        InlineKeyboardButton('Дальше➡',
                                             callback_data=str(callback.data)))
                    file = AsyncPath(str(photo[4]))
                    if await file.is_file():
                        async with aiofiles.open(str(photo[4]), 'rb') as file:
                            await callback.message.answer_photo(photo=file,
                                                                caption=photo[3],
                                                                reply_markup=keyboard)
                else:
                    await callback.answer(text='Нет заявок для модерации!',
                                          show_alert=True)
                    await callback.message.delete()
    except Exception as error:
        await callback.message.answer(
            text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!')
        logging.info(
            f'Error: {error}, user: {int(callback.from_user.id)}')


async def send_photos_to_channel(message: types.Message):
    try:
        region = await db.get_one(
            await queries.get_value(
                value='region',
                table='users'
            ),
            tg_id=int(message.from_user.id)
        )
        data = await db.get_all(queries.BP_NAME,
                                region=region[0],
                                is_active=False,
                                over=True)
        if data:
            await message.answer(text='Выберите практику для отправки '
                                      'фотографий в канал:',
                                 reply_markup=keyboards.back)
            for i in data:
                file = AsyncPath(str(i[4]))
                keyboard = InlineKeyboardMarkup()
                keyboard.insert(
                    InlineKeyboardButton('Отправить фото',
                                         callback_data=f'{i[0]}'))
                if await file.is_file():
                    async with aiofiles.open(str(i[4]), 'rb') as file:
                        await message.answer_photo(photo=file,
                                                   caption=f'<b>'
                                                           f'{str(i[0])}</b'
                                                           f'>\n\n'
                                                           f'{str(i[1])}',
                                                   reply_markup=keyboard)
                else:
                    await message.answer(text=f'<b>'
                                              f'{str(i[0])}</b>\n\n '
                                              f'{str(i[1])}',
                                         reply_markup=keyboard)
                await UserState.practice_send_to_channel_cm.set()
        else:
            await message.answer(
                text='Нет практик для отправки фото!\n'
                     'Практики в вашем регионе либо еще не завершились, '
                     'либо отсутствуют. ',
                reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def send_photos_to_channel_confirm(callback: types.CallbackQuery,
                                         state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    match callback.data:
        case 'bp_yes':
            await callback.message.delete()
            try:
                data = await state.get_data()
                await callback.bot.send_message(
                    chat_id=config.CHANNEL_ID,
                    text=f'Голосуйте за участников Лучшей Практики <b>"'
                         f'{data["bp_name"]}"</b>')
                await asyncio.sleep(2)
                photos = await db.get_all(queries.BP_PHOTOS,
                                          best_practice=data['bp_name'],
                                          kas_checked=True,
                                          kas_approved=True,
                                          cm_checked=True,
                                          cm_approved=True,
                                          active=True)
                for i in photos:
                    file = AsyncPath(str(i[4]))
                    if await file.is_file():
                        async with aiofiles.open(str(i[4]), 'rb') as photo:
                            await callback.bot.send_photo(
                                chat_id=config.CHANNEL_ID,
                                photo=photo,
                                caption=f'<b>{i[1]}</b>\n\n{i[3]}')
                            await asyncio.sleep(0.5)
                    else:
                        await callback.bot.send_message(
                            chat_id=config.CHANNEL_ID,
                            text=f'<b>{i[1]}</b>\n\n{i[3]}'
                        )
                        await asyncio.sleep(0.5)
                await callback.message.answer(text='Фото отправлены в канал!')
            except Exception as error:
                await callback.message.answer(
                    text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!')
                logging.info(
                    f'Error: {error}, user: {int(callback.from_user.id)}')
        case 'bp_no':
            await callback.message.delete()
        case _:
            await state.update_data(bp_name=str(callback.data))
            await callback.message.delete()
            await callback.message.answer(text=f'Вы уверены, что хотите '
                                               f'оправить фото практики '
                                               f'<u>{callback.data}</u> в '
                                               f'канал?',
                                          reply_markup=keyboards.confirm_keyboard)


async def make_suggest(message: types.Message):
    await message.answer(text='Здесь вы можете отправить '
                              'СитиМенеджеру предложения по Лучшим '
                              'Практикам.\n'
                              'Напишите и отправьте своё предложение или '
                              'нажмите "Назад".',
                         reply_markup=keyboards.back)
    try:
        position = await db.get_one(
            await queries.get_value(
                value='position',
                table='users'
            ),
            tg_id=int(message.from_user.id)
        )
        match position[0]:
            case 'mr':
                await UserState.practice_make_suggest_mr.set()
            case 'kas':
                await UserState.practice_make_suggest_kas.set()
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def send_suggest(message: types.Message):
    try:
        text_to_send = str(message.text)
        user = await db.get_one(queries.PROFILE,
                                tg_id=int(message.from_user.id))
        cm_tg_id = await db.get_one(
            await queries.get_value(
                value='tg_id',
                table='users'
            ),
            username=user[7]
        )
        if cm_tg_id[0]:
            await message.bot.send_message(chat_id=cm_tg_id[0],
                                           text=f'<b>Новое сообщение!</b>\n'
                                                f'<u>От:</u>  {user[0]}\n'
                                                f'<u>Тема:</u>  Предложения по '
                                                f'Лучшим '
                                                f'Практикам\n\n'
                                                f'{text_to_send}')
            await message.answer(text='Ваше предложение отправлено '
                                      'СитиМенеджеру!',
                                 reply_markup=keyboards.back)
        else:
            await message.answer(text='К сожалению ваш СитиМенеджер еще не '
                                      'подключен к боту, вы можете написать '
                                      'ему напрямую.',
                                 reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


def register_handlers_best_practice(dp: Dispatcher):
    dp.register_message_handler(practice_menu_mr,
                                text='Назад↩',
                                state=(UserState.practice_menu_mr,
                                       UserState.practice_make_suggest_mr,
                                       UserState.practice_take_part_mr_confirm,
                                       UserState.practice_take_part_mr_photo,
                                       UserState.practice_take_part_mr_desc))
    dp.register_message_handler(practice_menu_kas,
                                text='Назад↩',
                                state=(UserState.practice_menu_kas,
                                       UserState.practice_make_suggest_kas,
                                       UserState.practice_requests_show_kas))
    dp.register_message_handler(practice_menu_cm,
                                text='Назад↩',
                                state=(UserState.practice_menu_cm,
                                       UserState.practice_manage_cm,
                                       UserState.practice_manage_action_cm,
                                       UserState.practice_manage_change_name,
                                       UserState.practice_manage_change_desc,
                                       UserState.practice_manage_change_pic,
                                       UserState.practice_manage_change_start,
                                       UserState.practice_manage_change_stop,
                                       UserState.practice_requests_show_cm,
                                       UserState.practice_send_to_channel_cm,
                                       UserState.practice_add,
                                       UserState.practice_add_desc,
                                       UserState.practice_add_start,
                                       UserState.practice_add_stop,
                                       UserState.practice_add_picture))
    dp.register_message_handler(practice_menu_mr,
                                text='Практики🗣',
                                state=UserState.auth_mr)
    dp.register_message_handler(practice_menu_kas,
                                text='Практики🗣',
                                state=UserState.auth_kas)
    dp.register_message_handler(practice_menu_cm,
                                text='Практики🗣',
                                state=UserState.auth_cm)
    dp.register_message_handler(get_current_practice,
                                text='Текущие практики🎯',
                                state=UserState.practice_menu_mr)
    dp.register_callback_query_handler(take_part,
                                       state=UserState.practice_menu_mr)
    dp.register_callback_query_handler(take_part_confirmation,
                                       state=UserState.practice_take_part_mr_confirm)
    dp.register_message_handler(take_part_take_photo,
                                content_types=['photo'],
                                state=UserState.practice_take_part_mr_photo)
    dp.register_message_handler(take_part_take_description,
                                state=UserState.practice_take_part_mr_desc)
    dp.register_message_handler(manage_practice,
                                text='Управлять текущими🔀',
                                state=UserState.practice_menu_cm)
    dp.register_callback_query_handler(select_action_manage,
                                       state=UserState.practice_manage_cm)
    dp.register_callback_query_handler(action_manage,
                                       state=UserState.practice_manage_action_cm)
    dp.register_message_handler(manage_change_name,
                                state=UserState.practice_manage_change_name)
    dp.register_message_handler(manage_change_desc,
                                state=UserState.practice_manage_change_desc)
    dp.register_message_handler(manage_change_pic,
                                content_types=['photo'],
                                state=UserState.practice_manage_change_pic)
    dp.register_message_handler(manage_change_start,
                                state=UserState.practice_manage_change_start)
    dp.register_message_handler(manage_change_stop,
                                state=UserState.practice_manage_change_stop)
    dp.register_message_handler(add_new_practice_add_name,
                                text='Добавить новую➕',
                                state=UserState.practice_menu_cm)
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

    dp.register_message_handler(send_photos_to_channel,
                                text='Отправить фото в канал⤴',
                                state=UserState.practice_menu_cm)
    dp.register_callback_query_handler(send_photos_to_channel_confirm,
                                       state=UserState.practice_send_to_channel_cm)

    dp.register_message_handler(practice_requests_kas,
                                text='Смотреть заявки📬',
                                state=UserState.practice_menu_kas)
    dp.register_callback_query_handler(practice_requests_show_kas,
                                       state=UserState.practice_requests_show_kas)
    dp.register_message_handler(practice_requests_cm,
                                text='Смотреть заявки📬',
                                state=UserState.practice_menu_cm)
    dp.register_callback_query_handler(practice_requests_show_cm,
                                       state=UserState.practice_requests_show_cm)
    dp.register_message_handler(make_suggest,
                                text='Предложения📝',
                                state=(UserState.practice_menu_mr,
                                       UserState.practice_menu_kas))
    dp.register_message_handler(send_suggest,
                                state=(UserState.practice_make_suggest_mr,
                                       UserState.practice_make_suggest_kas))
