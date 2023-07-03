import aiofiles
import datetime
import locale
import logging
from aiopath import AsyncPath
from aiofiles import os as aios
from itertools import cycle

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
            confirm_keyboard = InlineKeyboardMarkup()
            confirm_keyboard.insert(
                InlineKeyboardButton('Да',
                                     callback_data='bp_yes'))
            confirm_keyboard.insert(
                InlineKeyboardButton('Нет',
                                     callback_data='bp_no'))
            await state.update_data(bp_name=str(callback.data))
            await state.update_data(username=str(username[0]))
            await callback.message.answer(text=f'Вы уверены, что хотите '
                                               f'участвовать в практике:\n'
                                               f'<b>{callback.data}?</b>',
                                          reply_markup=confirm_keyboard)
            await UserState.practice_take_part_mr_confirm.set()
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def take_part_confirmation(callback: types.CallbackQuery):
    await callback.bot.answer_callback_query(callback.id)
    if callback.data == 'bp_yes':
        await callback.message.answer(text='Отправьте фотографию:')
        await UserState.practice_take_part_mr_photo.set()
    if callback.data == 'bp_no':
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
        destination = f'./files/best_practice/{int(bp_id[0])}/{int(message.from_user.id)}.jpg '
        await state.update_data(destination=destination)
        await message.photo[-1].download(destination_file=destination,
                                         make_dirs=True)
        await message.answer(text='Добавьте описание к фото',
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
                                is_active=True)
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
    data = await state.get_data()
    print(data)
    if callback.data == 'Accept':
        await callback.bot.answer_callback_query(callback.id)
        await db.post(queries.BP_KAS,
                      kas_checked=True,
                      kas_approved=True,
                      id=data['bp_id'])
        await callback.bot.send_message(chat_id=data['mr_tg_id'],
                                        text='✅ Ваша заявка на участие в '
                                             'Лучшей Практике принята '
                                             'Супервайзером!')
    elif callback.data == 'Decline':
        await callback.bot.answer_callback_query(callback.id)
        await db.post(queries.BP_KAS,
                      kas_checked=True,
                      kas_approved=False,
                      id=data['bp_id'])
        await callback.bot.send_message(chat_id=data['mr_tg_id'],
                                        text='❗ Ваша заявка на участие в '
                                             'Лучшей Практике отклонена '
                                             'Супервайзером!')
    else:
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
            await state.update_data(mr_tg_id=photo[1])

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
            file = AsyncPath(str(photo[3]))
            if await file.is_file():
                async with aiofiles.open(str(photo[3]), 'rb') as file:
                    await callback.message.answer_photo(photo=file,
                                                        caption=f'{photo[2]}',
                                                        reply_markup=keyboard)
        else:
            await callback.answer(text='Нет фото для модерации!',
                                  show_alert=True)
            await callback.message.delete()


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
                                is_active=True)
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
    data = await state.get_data()
    print(data)
    if callback.data == 'Accept':
        await callback.bot.answer_callback_query(callback.id)
        await db.post(queries.BP_CM,
                      cm_checked=True,
                      cm_approved=True,
                      id=data['bp_id'])
        await callback.bot.send_message(chat_id=data['mr_tg_id'],
                                        text='✅ Ваша заявка на участие в '
                                             'Лучшей Практике принята '
                                             'СитиМенеджером!')
    elif callback.data == 'Decline':
        await callback.bot.answer_callback_query(callback.id)
        await db.post(queries.BP_CM,
                      cm_checked=True,
                      cm_approved=False,
                      id=data['bp_id'])
        await callback.bot.send_message(chat_id=data['mr_tg_id'],
                                        text='❗ Ваша заявка на участие в '
                                             'Лучшей Практике отклонена '
                                             'СитиМенеджером!')
    else:
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
            await state.update_data(mr_tg_id=photo[1])

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
            file = AsyncPath(str(photo[3]))
            if await file.is_file():
                async with aiofiles.open(str(photo[3]), 'rb') as file:
                    await callback.message.answer_photo(photo=file,
                                                        caption=f'{photo[2]}',
                                                        reply_markup=keyboard)
        else:
            await callback.answer(text='Нет фото для модерации!',
                                  show_alert=True)
            await callback.message.delete()


async def make_suggest(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


def register_handlers_best_practice(dp: Dispatcher):
    dp.register_message_handler(practice_menu_mr,
                                text='Назад↩',
                                state=(UserState.practice_menu_mr,
                                       UserState.practice_take_part_mr_confirm,
                                       UserState.practice_take_part_mr_photo,
                                       UserState.practice_take_part_mr_desc))

    dp.register_message_handler(practice_menu_kas,
                                text='Назад↩',
                                state=(UserState.practice_menu_kas,
                                       UserState.practice_requests_show_kas))

    dp.register_message_handler(practice_menu_cm,
                                text='Назад↩',
                                state=(UserState.practice_menu_cm,
                                       UserState.practice_requests_show_cm,
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
                                       UserState.practice_menu_kas,
                                       UserState.practice_menu_cm))
