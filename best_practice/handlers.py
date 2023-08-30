import asyncio
import locale
import uuid
from datetime import datetime as dt
import aiofiles
from aiofiles import os as aios
from aiopath import AsyncPath


from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    InputMediaPhoto


import config
from loader import db
from users.handlers import get_value_by_tgig
from utils import decorators, keyboards, queries, jobs
from utils.states import UserState

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


async def practice_menu_mr(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer(
        text='Выберите пункт из меню:',
        reply_markup=keyboards.practice_menu_mr)
    await UserState.practice_menu_mr.set()


async def practice_menu_kas(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer(
        text='Выберите пункт из меню:',
        reply_markup=keyboards.practice_menu_kas)
    await UserState.practice_menu_kas.set()


async def practice_menu_cm(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer(
        text='Выберите пункт из меню:',
        reply_markup=keyboards.practice_menu_cm)
    await UserState.practice_menu_cm.set()


@decorators.error_handler_message
async def manage_practice(message: types.Message, state: FSMContext):
    data = await db.get_all(
        await queries.get_value(
            value='*',
            table='best_practice'),
        region=await get_value_by_tgig(
            value='region',
            table='users',
            tg_id=int(message.from_user.id)),
        is_over=False)
    if data:
        await message.answer(
            text='Выберите практику для управления:',
            reply_markup=keyboards.back)
        for i in data:
            start, stop = await jobs.datetime_op(i[6], i[7])
            keyboard = InlineKeyboardMarkup()
            keyboard.insert(
                InlineKeyboardButton('Управлять',
                                     callback_data=f'{i[2]}'))
            file = AsyncPath(str(i[8]))
            if await file.is_file():
                async with aiofiles.open(file, 'rb') as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=f'<b>{str(i[2])}</b>\n\n{str(i[3])}\n\n'
                                f'<b>Дата начала:</b>\n{str(start)}\n\n'
                                f'<b>Дата окончания:</b>\n{str(stop)}',
                        reply_markup=keyboard)
            else:
                await message.answer(
                    text=f'<b>{str(i[2])}</b>\n\n{str(i[3])}\n\n'
                         f'<b>Дата начала:</b>\n{str(start)}\n\n'
                         f'<b>Дата окончания:</b>\n{str(stop)}',
                    reply_markup=keyboard)
            await UserState.practice_manage_cm.set()
    else:
        await message.answer(
            text='Нет практик для управления!',
            reply_markup=keyboards.back)


async def select_action_manage(callback: types.CallbackQuery,
                               state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    await state.update_data(bp_name=str(callback.data))
    await callback.message.edit_reply_markup(
        reply_markup=keyboards.manage_keyboard)
    await UserState.practice_manage_action_cm.set()


async def action_manage(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    data = await state.get_data()
    match callback.data:
        case 'change_name':
            await callback.message.delete_reply_markup()
            await callback.message.answer(
                text='Введите новое название для практики:\n'
                     '(Не более 45 символов, вместе с пробелами!)')
            await UserState.practice_manage_change_name.set()

        case 'change_desc':
            await callback.message.delete_reply_markup()
            await callback.message.answer(
                text='Введите новое описание для практики:')
            await UserState.practice_manage_change_desc.set()
        case 'change_pic':
            await callback.message.delete_reply_markup()
            await callback.message.answer(
                text='Отправьте новую фотографию:')
            await UserState.practice_manage_change_pic.set()
        case 'change_start':
            await callback.message.delete_reply_markup()
            await callback.message.answer(
                    text='Введите новую дату начала в формате "20-01-2003":')
            await UserState.practice_manage_change_start.set()
        case 'change_stop':
            await callback.message.delete_reply_markup()
            await callback.message.answer(
                text='Введите новую дату окончания в формате "20-01-2003":')
            await UserState.practice_manage_change_stop.set()
        case 'delete_bp':
            await callback.message.answer(
                text=f'Вы действительно хотите удалить практику '
                     f'<b><u>{data["bp_name"]}?</u></b>',
                reply_markup=keyboards.confirm_keyboard)
        case 'bp_yes':
            await db.post(
                queries.DELETE_BP,
                name=data['bp_name'])
            await callback.message.delete()
            await callback.message.answer(
                text='Практика успешно удалена!',
                reply_markup=keyboards.back)
        case 'bp_no':
            await callback.message.delete()


@decorators.error_handler_message
async def manage_change_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = str(message.text)
    if len(name) > 45:
        await message.answer(text='❗ Превышен лимит в 45 символов!')
    else:
        check_name = await db.get_one(
            await queries.get_value(
                value='name',
                table='best_practice'),
            name=name)
        if check_name:
            await message.answer(
                text='❗ Практика с таким названием уже существует!\n'
                     'Введите другое название!')
        else:
            await db.post(
                await queries.update_value(
                    table='best_practice',
                    column_name='name',
                    where_name='name'),
                new_name=name,
                old_name=data['bp_name']
            )
            await message.answer(text='Название успешно изменено!')



@decorators.error_handler_message
async def manage_change_desc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await db.post(
        await queries.update_value(
            table='best_practice',
            column_name='desc',
            where_name='name'),
        desc=str(message.text),
        name=data['bp_name']
    )
    await message.answer(text='Описание успешно изменено!')


@decorators.error_handler_message
async def manage_change_pic(message: types.Message, state: FSMContext):
    data = await state.get_data()
    destination = await db.get_one(
        await queries.get_value(
            value='file_link',
            table='best_practice'),
        name=data['bp_name'])
    await message.photo[-1].download(
        destination_file=destination[0],
        make_dirs=True)
    await message.answer(text='Фотография успешно изменена!')


@decorators.error_handler_message
async def manage_change_start(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        date_start = dt.strptime(str(message.text), '%d-%m-%Y')
        if date_start < dt.now():
            await message.answer(
                text='❗ Дата начала должна быть позднее текущей даты!\n'
                     'Введите дату еще раз!')
        else:
            await db.post(
                await queries.update_value(
                    table='best_practice',
                    column_name='datetime_start',
                    where_name='name'),
                datetime_start=date_start,
                name=data['bp_name'])
            await message.answer(text='Дата начала успешно изменена!')
    except ValueError:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')


@decorators.error_handler_message
async def manage_change_stop(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        date_stop = dt.strptime(str(message.text), '%d-%m-%Y')
        if date_stop < dt.now():
            await message.answer(
                text='❗ Дата окончания должна быть позднее текущей даты!\n'
                     'Введите дату еще раз!')
        else:
            date_start = await db.get_one(
                await queries.get_value(
                    value='datetime_start',
                    table='best_practice'),
                name=data['bp_name'])
            date_start = dt.strptime(date_start[0], '%Y-%m-%d %H:%M:%S')
            if date_stop < date_start:
                await message.answer(
                    text='❗ Дата окончания должна быть позднее даты начала!\n'
                         'Введите дату еще раз!')
            else:
                await db.post(
                    await queries.update_value(
                        table='best_practice',
                        column_name='datetime_stop',
                        where_name='name'),
                    datetime_stop=date_stop,
                    name=data['bp_name'])
                await message.answer(text='Дата окончания успешно изменена!')
    except ValueError:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')


@decorators.error_handler_message
async def get_current_practice(message: types.Message, state: FSMContext):
    data = await db.get_all(
        await queries.get_value(
            value='*',
            table='best_practice'),
        region=await get_value_by_tgig(
            value='region',
            table='users',
            tg_id=int(message.from_user.id)),
        is_active=True,
        is_over=False)
    if data:
        await message.answer(
            text='Практики вашего региона, доступные для участия на данный '
                 'момент:',
            reply_markup=keyboards.back)
        for i in data:
            start, stop = await jobs.datetime_op(i[6], i[7])
            inline_keyboard = InlineKeyboardMarkup()
            inline_keyboard.insert(
                InlineKeyboardButton('Участвовать!📨',
                                     callback_data=f'{i[2]}'))
            file = AsyncPath(str(i[8]))
            if await file.is_file():
                async with aiofiles.open(file, 'rb') as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=f'<b>{str(i[2])}</b>\n\n{str(i[3])}\n\n'
                                f'<b>Дата начала:</b>\n{str(start)}\n\n'
                                f'<b>Дата окончания:</b>\n{str(stop)}',
                        reply_markup=inline_keyboard)
            else:
                await message.answer(
                    f'{str(i[2])}</b>\n\n{str(i[3])}\n\n'
                    f'<b>Дата начала:</b>\n{str(start)}\n\n'
                    f'<b>Дата окончания:</b>\n{str(stop)}',
                    reply_markup=inline_keyboard)
    else:
        await message.answer(
            text='Доступных практик в вашем регионе на данный момент нет!',
            reply_markup=keyboards.back)



@decorators.error_handler_callback
async def take_part(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    await state.update_data(bp_name=str(callback.data))
    await callback.message.answer(
        text=f'Вы уверены, что хотите участвовать в практике:\n'
             f'<b>{callback.data}?</b>',
        reply_markup=keyboards.confirm_keyboard)
    await UserState.practice_take_part_mr_confirm.set()



async def take_part_confirmation(callback: types.CallbackQuery):
    await callback.bot.answer_callback_query(callback.id)
    await callback.message.delete()
    match callback.data:
        case 'bp_yes':
            await callback.message.answer(
                text='Отправьте фотографию для участия:')
            await UserState.practice_take_part_mr_photo.set()
        case 'bp_no':
            await UserState.practice_menu_mr.set()


@decorators.error_handler_message
async def take_part_take_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    bp_id = await db.get_one(
        await queries.get_value(
            value='id',
            table='best_practice'),
        name=str(data['bp_name']))
    destination = f'./files/best_practice/{int(bp_id[0])}/' \
                  f'{uuid.uuid1()}.jpg '
    await state.update_data(destination=destination)
    await state.update_data(bp_id=bp_id[0])
    await message.photo[-1].download(
        destination_file=destination,
        make_dirs=True)
    await message.answer(
        text='Добавьте комментарий к фото',
        reply_markup=keyboards.back)
    await UserState.practice_take_part_mr_desc.set()



@decorators.error_handler_message
async def take_part_take_description(message: types.Message,
                                     state: FSMContext):
    data = await state.get_data()
    username = await get_value_by_tgig(
        value='username',
        table='users',
        tg_id=int(message.from_user.id))
    kas = await get_value_by_tgig(
        value='kas',
        table='users',
        tg_id=int(message.from_user.id))
    kas_tg_id = await db.get_one(
        await queries.get_value(
            value='tg_id',
            table='users'),
        position='kas',
        username=await get_value_by_tgig(
            value='kas',
            table='users',
            tg_id=int(message.from_user.id)))
    await db.post(queries.INSERT_PRACTICE_MR,
                  bp_id=str(data['bp_id']),
                  username=username,
                  kas=kas,
                  tg_id=int(message.from_user.id),
                  datetime_added=dt.now(),
                  desc=str(message.text),
                  file_link=str(data['destination']))

    await message.answer(
        text='Ваше заявка принята, ожидайте решения!',
        reply_markup=keyboards.back)
    await message.bot.send_message(
        chat_id=kas_tg_id[0],
        text='🆕 Поступила новая заявка для участия в Лучшей '
             'Практике!')


async def add_new_practice_add_name(message: types.Message):
    await message.answer(
        text='Введите уникальное название новой практики:\n'
             '(Не более 45 символов, вместе с пробелами!)',
        reply_markup=keyboards.back)
    await UserState.practice_add.set()


@decorators.error_handler_message
async def add_new_practice_add_desc(message: types.Message, state: FSMContext):
    name = str(message.text)
    if len(name) > 45:
        await message.answer(text='❗ Превышен лимит в 45 символов!\n'
                                  'Введите название еще раз!')
    else:
        check_name = await db.get_one(
            await queries.get_value(
                value='name',
                table='best_practice'),
            name=name)
        if check_name:
            await message.answer(
                text='❗ Практика с таким названием уже существует!\n'
                     'Введите другое название!')
        else:
            await state.update_data(name=name)
            await message.answer(
                text='Добавьте описание для новой практики:',
                reply_markup=keyboards.back)
            await UserState.practice_add_desc.set()



async def add_new_practice_add_start(message: types.Message,
                                     state: FSMContext):
    await state.update_data(desc=str(message.text))
    await message.answer(
        text='Введите дату <u>начала</u> в формате "20-01-2003":',
        reply_markup=keyboards.back)
    await UserState.practice_add_start.set()


async def add_new_practice_add_stop(message: types.Message, state: FSMContext):
    try:
        date_start = dt.strptime(str(message.text), '%d-%m-%Y')
        if date_start < dt.now():
            await message.answer(
                text='❗ Дата начала должна быть позднее текущей даты!\n'
                     'Введите дату еще раз!')
        else:
            await state.update_data(
                date_start=date_start.strftime('%Y-%m-%d %H:%M:%S'))
            await message.answer(
                text='Введите дату <u>окончания</u> в формате "20-01-2003":',
                reply_markup=keyboards.back)
            await UserState.practice_add_stop.set()
    except ValueError:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')


async def add_new_practice_add_picture(message: types.Message,
                                       state: FSMContext):
    try:
        date_stop = dt.strptime(str(message.text), '%d-%m-%Y')
        if date_stop < dt.now():
            await message.answer(
                text='❗ Дата окончания должна быть позднее текущей даты!\n'
                     'Введите дату еще раз!')
        else:
            data = await state.get_data()
            date_start = dt.strptime(data['date_start'], '%Y-%m-%d %H:%M:%S')
            if date_stop <= date_start:
                await message.answer(
                    text='❗ Дата окончания должна быть позднее даты начала!\n'
                         'Введите дату еще раз!')
            else:
                await state.update_data(
                    date_stop=date_stop.strftime('%Y-%m-%d %H:%M:%S'))
                await message.answer(
                    text='Добавьте фотографию для новой практики:',
                    reply_markup=keyboards.back)
                await UserState.practice_add_picture.set()
    except ValueError:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')


@decorators.error_handler_message
async def add_new_practice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = await get_value_by_tgig(
        value='*',
        table='users',
        tg_id=int(message.from_user.id))
    max_id = await db.get_one(
        await queries.get_value(
            value='MAX(id)',
            table='best_practice'))
    if max_id[0] is None:
        max_id = ('0',)
    destination = f'./files/best_practice/{int(max_id[0]) + 1}/1.jpg'
    await message.photo[-1].download(
        destination_file=destination,
        make_dirs=True)
    await db.post(
        queries.INSERT_PRACTICE,
        region=user[5],
        name=data['name'],
        desc=data['desc'],
        user_added=user[1],
        datetime_added=dt.now(),
        datetime_start=data['date_start'],
        datetime_stop=data['date_stop'],
        file_link=destination)
    await message.answer(
        text=f'Новая лучшая практика <b>{data["name"]}</b> успешно добавлена!',
        reply_markup=keyboards.back)


# просмотр заявок для модерации супервайзером
@decorators.error_handler_message
async def practice_requests_kas(message: types.Message, state: FSMContext):
    data = await db.get_all(
        await queries.get_value(
            value='*',
            table='best_practice'),
        region=await get_value_by_tgig(
            value='region',
            table='users',
            tg_id=int(message.from_user.id)),
        is_active=True,
        is_v_active=False)
    if data:
        await message.answer(
            text='Практики, доступные на данный момент:',
            reply_markup=keyboards.back)
        for i in data:
            inline_keyboard = InlineKeyboardMarkup()
            inline_keyboard.insert(
                InlineKeyboardButton('Смотреть заявки👀',
                                     callback_data=f'{i[0]}'))
            await message.answer(
                text=f'<b>{i[2]}</b>',
                reply_markup=inline_keyboard)
            await UserState.practice_requests_show_kas.set()
    else:
        await message.answer(
            text='Доступных практик на данный момент нет!',
            reply_markup=keyboards.back)


# обработка модерации заявок супервайзером
@decorators.error_handler_callback
async def practice_requests_show_kas(callback: types.CallbackQuery,
                                     state: FSMContext):
    if callback.data not in ('Accept', 'Decline'):
        await state.update_data(bp_id=str(callback.data))
    data = await state.get_data()
    match callback.data:
        case 'Accept':
            cm_tg_id = await db.get_one(
                await queries.get_value(
                    value='tg_id',
                    table='users'),
                position='cm',
                username = await get_value_by_tgig(
                    value='citimanager',
                    table='users',
                    tg_id=int(callback.from_user.id)))
            await db.post(
                queries.BP_KAS,
                kas_approved=True,
                id=data['bp_mr_id'])
            await callback.answer(
                text='Заявка принята!',
                show_alert=False)
            await callback.bot.send_message(
                chat_id=data['mr_tg_id'],
                text='✅ Ваша заявка на участие в Лучшей Практике принята'
                     ' Супервайзером!')
            await callback.bot.send_message(
                chat_id=cm_tg_id[0],
                text='🆕 Поступила новая заявка для участия в Лучшей '
                     'Практике!')
            await asyncio.sleep(0.1)
            bp_mr = await db.get_one(
                await queries.get_value(
                    value='*',
                    table='best_practice_mr'),
                bp_id=data['bp_id'],
                kas=data['kas'],
                kas_approved=False)
            if bp_mr:
                await state.update_data(bp_mr_id=bp_mr[0])
                await state.update_data(mr_tg_id=bp_mr[4])
                file = AsyncPath(str(bp_mr[7]))
                if await file.is_file():
                    with open(file, 'rb') as photo:
                        await callback.message.edit_media(
                            media=InputMediaPhoto(
                                media=photo,
                                caption=bp_mr[6]),
                            reply_markup=keyboards.accept_keyboard)
            else:
                await callback.message.answer(
                    text='Больше нет заявок для модерации!')
                await callback.message.delete()
        case 'Decline':
            file_path = await db.get_one(
                await queries.get_value(
                    value='file_link',
                    table='best_practice_mr'),
                id=data['bp_mr_id'])
            await aios.remove(file_path[0])
            await db.post(
                queries.DELETE_BP_MR,
                id=data['bp_mr_id'])
            await callback.answer(
                text='Заявка отклонена!',
                show_alert=False)
            await callback.bot.send_message(
                chat_id=data['mr_tg_id'],
                text='❗ Ваша заявка на участие в Лучшей Практике отклонена'
                     ' Супервайзером!\n\nВы можете попробовать еще раз!')
            await asyncio.sleep(0.1)
            bp_mr = await db.get_one(
                await queries.get_value(
                    value='*',
                    table='best_practice_mr'),
                bp_id=data['bp_id'],
                kas=data['kas'],
                kas_approved=False)
            if bp_mr:
                await state.update_data(bp_mr_id=bp_mr[0])
                await state.update_data(mr_tg_id=bp_mr[4])
                file = AsyncPath(str(bp_mr[7]))
                if await file.is_file():
                    with open(file, 'rb') as photo:
                        await callback.message.edit_media(
                            media=InputMediaPhoto(
                                media=photo,
                                caption=bp_mr[6]),
                            reply_markup=keyboards.accept_keyboard)
            else:
                await callback.message.answer(
                    text='Больше нет заявок для модерации!')
                await callback.message.delete()
        case _:
            kas = await get_value_by_tgig(
                value='username',
                table='users',
                tg_id=int(callback.from_user.id))
            bp_mr = await db.get_one(
                await queries.get_value(
                    value='*',
                    table='best_practice_mr'),
                bp_id=data['bp_id'],
                kas=kas,
                kas_approved=False)
            if bp_mr:
                await callback.message.delete()
                await callback.message.answer_chat_action(
                    action='upload_photo')
                await state.update_data(bp_mr_id=bp_mr[0])
                await state.update_data(mr_tg_id=bp_mr[4])
                await state.update_data(kas=kas)
                file = AsyncPath(str(bp_mr[7]))
                if await file.is_file():
                    async with aiofiles.open(file, 'rb') as photo:
                        await callback.message.answer_photo(
                            photo=photo,
                            caption=bp_mr[6],
                            reply_markup=keyboards.accept_keyboard)
            else:
                await callback.answer(
                    text='Нет заявок для модерации!',
                    show_alert=True)
                await callback.message.delete()


# просмотр заявок для модерации ситименджером
@decorators.error_handler_message
async def practice_requests_cm(message: types.Message, state: FSMContext):
    data = await db.get_all(
        await queries.get_value(
            value='*',
            table='best_practice'),
        region=await get_value_by_tgig(
            value='region',
            table='users',
            tg_id=int(message.from_user.id)),
        is_active=True,
        is_v_active=False)
    if data:
        await message.answer(
            text='Практики, доступные на данный момент:',
            reply_markup=keyboards.back)
        for i in data:
            inline_keyboard = InlineKeyboardMarkup()
            inline_keyboard.insert(
                InlineKeyboardButton('Смотреть заявки👀',
                                     callback_data=f'{i[0]}'))
            await message.answer(
                text=f'<b>{i[2]}</b>',
                reply_markup=inline_keyboard)
            await UserState.practice_requests_show_cm.set()
    else:
        await message.answer(
            text='Доступных практик на данный момент нет!',
            reply_markup=keyboards.back)


# обработка модерации заявок ситименеджером
@decorators.error_handler_callback
async def practice_requests_show_cm(callback: types.CallbackQuery,
                                    state: FSMContext):
    if callback.data not in ('Accept', 'Decline'):
        await state.update_data(bp_id=str(callback.data))
    data = await state.get_data()
    match callback.data:
        case 'Accept':
            await db.post(
                queries.BP_CM,
                cm_approved=True,
                id=data['bp_mr_id'])
            await callback.answer(
                text='Заявка принята!',
                show_alert=False)
            await callback.bot.send_message(
                chat_id=data['mr_tg_id'],
                text='✅ Ваша заявка на участие в Лучшей Практике принята'
                     ' СитиМенеджером!')
            await callback.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text='Новая заявка для участия в Лучшей Практике')
            await callback.bot.send_photo(
                chat_id=config.CHANNEL_ID,
                photo=data['bp_mr_photo'],
                caption=data['bp_desc'])
            await asyncio.sleep(0.1)
            bp_mr = await db.get_one(
                await queries.get_value(
                    value='*',
                    table='best_practice_mr'),
                best_practice=data['bp_name'],
                kas_approved=True,
                cm_approved=False)
            if bp_mr:
                await state.update_data(bp_id=bp_mr[0])
                await state.update_data(mr_tg_id=bp_mr[4])
                await state.update_data(bp_mr_photo=bp_mr[7])
                await state.update_data(bp_desc=bp_mr[6])
                file = AsyncPath(str(bp_mr[7]))
                if await file.is_file():
                    with open(file, 'rb') as photo:
                        await callback.message.edit_media(
                            media=InputMediaPhoto(
                                media=photo,
                                caption=bp_mr[6]),
                            reply_markup=keyboards.accept_keyboard)
            else:
                await callback.message.answer(
                    text='Больше нет заявок для модерации!')
                await callback.message.delete()
        case 'Decline':
            await db.post(queries.DELETE_BP_MR,
                          id=data['bp_id'])
            await callback.answer(
                text='Заявка отклонена!',
                show_alert=False)
            await callback.bot.send_message(
                chat_id=data['mr_tg_id'],
                text='❗ Ваша заявка на участие в Лучшей Практике отклонена'
                     ' СитиМенеджером!\n\nВы можете попробовать еще раз!')
            await asyncio.sleep(0.1)
            bp_mr = await db.get_one(
                await queries.get_value(
                    value='*',
                    table='best_practice_mr'),
                best_practice=data['bp_name'],
                kas_approved=True,
                cm_approved=False)
            if bp_mr:
                await state.update_data(bp_id=bp_mr[0])
                await state.update_data(mr_tg_id=bp_mr[4])
                await state.update_data(bp_mr_photo=bp_mr[7])
                await state.update_data(bp_desc=bp_mr[6])
                file = AsyncPath(str(bp_mr[7]))
                if await file.is_file():
                    with open(file, 'rb') as photo:
                        await callback.message.edit_media(
                            media=InputMediaPhoto(
                                media=photo,
                                caption=bp_mr[6]),
                            reply_markup=keyboards.accept_keyboard)
            else:
                await callback.message.answer(
                    text='Больше нет заявок для модерации!')
                await callback.message.delete()
        case _:
            bp_mr = await db.get_one(
                await queries.get_value(
                    value='*',
                    table='best_practice_mr'),
                best_practice=str(callback.data),
                kas_approved=True,
                cm_approved=False)
            if bp_mr:
                await callback.message.delete()
                await callback.message.answer_chat_action(
                    action='upload_photo')
                await state.update_data(bp_id=bp_mr[0])
                await state.update_data(mr_tg_id=bp_mr[4])
                await state.update_data(bp_mr_photo=bp_mr[7])
                await state.update_data(bp_desc=bp_mr[6])
                file = AsyncPath(str(bp_mr[7]))
                if await file.is_file():
                    async with aiofiles.open(file, 'rb') as photo:
                        await callback.message.answer_photo(
                            photo=photo,
                            caption=bp_mr[6],
                            reply_markup=keyboards.accept_keyboard)
            else:
                await callback.answer(
                    text='Нет заявок для модерации!',
                    show_alert=True)
                await callback.message.delete()


# меню голосования
async def practice_vote_menu_cm(message: types.Message, state: FSMContext):
    await message.answer(
        text='Выберите пункт из меню:',
        reply_markup=keyboards.vote_menu_cm)
    await UserState.practice_vote_menu_cm.set()


# обработка нажатия открыть голосование
@decorators.error_handler_message
async def practice_start_voting(message: types.Message, state: FSMContext):
    data = await db.get_all(
        await queries.get_value(
            value='*',
            table='best_practice'),
        region=await get_value_by_tgig(
            value='region',
            table='users',
            tg_id=int(message.from_user.id)),
        is_active=True,
        is_over=True,
        is_v_active=False,
        is_v_over=False)
    if data:
        await message.answer(
            text='Выберите практику для старта голосования:\n'
                 '(Сразу после старта все заявки, прошедшие модерацию '
                 'автоматически отправятся в ТГ-канал региона!)',
            reply_markup=keyboards.back)
        for i in data:
            keyboard = InlineKeyboardMarkup()
            keyboard.insert(
                InlineKeyboardButton('Начать голосование',
                                     callback_data=f'{i[0]}'))
            file = AsyncPath(str(i[8]))
            if await file.is_file():
                async with aiofiles.open(file, 'rb') as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=f'<b>{str(i[2])}</b>\n\n{str(i[3])}',
                        reply_markup=keyboard)
            else:
                await message.answer(
                    text=f'<b>{str(i[2])}</b>\n\n{str(i[3])}',
                    reply_markup=keyboard)
        await UserState.practice_start_voting.set()
    else:
        await message.answer(
            text='Нет практик для старта голосования!\n'
                 'Практики в вашем регионе либо еще не завершились, '
                 'либо отсутствуют. ',
            reply_markup=keyboards.back)


# старт голосования и отправка инфы в канал
@decorators.error_handler_callback
async def practice_start_voting_send(callback: types.CallbackQuery,
                                         state: FSMContext):
    bp_id = int(callback.data)
    await callback.message.delete()
    await db.post(
        await queries.update_value(
            table='best_practice',
            column_name='is_v_active',
            where_name='id'),
        is_v_active=True,
        id=bp_id)
    photos = await db.get_all(
        await queries.get_value(
            value='*',
            table='best_practice_mr'),
        bp_id=bp_id,
        kas_approved=True,
        cm_approved=True,
        posted=False)
    if photos:
        bp_name = await db.get_one(
            await queries.get_value(
                value='name',
                table='best_practice'),
            id=bp_id)
        await callback.bot.send_message(
            chat_id=config.CHANNEL_ID,
            text=f'Началось голосование за участников Лучшей Практики <b>'
                 f'{bp_name[0]}</b>!')
        await asyncio.sleep(1)
        for i in photos:
            vote_keyboard = InlineKeyboardMarkup()
            vote_keyboard.insert(
                InlineKeyboardButton('Поставить Лайк 👍🏻',
                                     callback_data=f'bp_vote_{i[0]}'))
            file = AsyncPath(str(i[7]))
            if await file.is_file():
                async with aiofiles.open(file, 'rb') as photo:
                    await callback.bot.send_photo(
                        chat_id=config.CHANNEL_ID,
                        photo=photo,
                        caption=i[6],
                        reply_markup=vote_keyboard)
                    await asyncio.sleep(0.1)
            else:
                await callback.bot.send_message(
                    chat_id=config.CHANNEL_ID,
                    text=f'<b>{i[6]}')
                await asyncio.sleep(0.1)
            await db.post(
                await queries.update_value(
                    table='best_practice_mr',
                    column_name='posted',
                    where_name='id'),
                posted=True,
                id=i[0])
        await callback.message.answer(
            text='Голосование началось, заявки отправлены в канал!')
    else:
        await callback.answer(
            text='Нет заявок для голосования!',
            show_alert=True)


# обработка нажатия закрыть голосование
@decorators.error_handler_message
async def practice_stop_voting(message: types.Message, state: FSMContext):
    data = await db.get_all(
        await queries.get_value(
            value='*',
            table='best_practice'),
        region=await get_value_by_tgig(
            value='region',
            table='users',
            tg_id=int(message.from_user.id)),
        is_active=True,
        is_over=True,
        is_v_active=True,
        is_v_over=False)
    if data:
        await message.answer(
            text='Выберите практику для остановки голосования:',
            reply_markup=keyboards.back)
        for i in data:
            keyboard = InlineKeyboardMarkup()
            keyboard.insert(
                InlineKeyboardButton('Остановить голосование',
                                     callback_data=f'{i[0]}'))
            file = AsyncPath(str(i[8]))
            if await file.is_file():
                async with aiofiles.open(file, 'rb') as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=f'<b>{str(i[2])}</b>\n\n{str(i[3])}',
                        reply_markup=keyboard)
            else:
                await message.answer(
                    text=f'<b>{str(i[2])}</b>\n\n{str(i[3])}',
                    reply_markup=keyboard)
        await UserState.practice_stop_voting.set()
    else:
        await message.answer(
            text='Нет практик для остановки голосования!\n'
                 'Практики в вашем регионе либо еще не завершились, '
                 'либо отсутствуют. ',
            reply_markup=keyboards.back)


# остановка голосования и отправка инфы в канал
@decorators.error_handler_callback
async def practice_stop_voting_send(callback: types.CallbackQuery,
                                         state: FSMContext):
    bp_id = int(callback.data)
    await callback.message.delete()
    await db.post(
        await queries.update_value(
            table='best_practice',
            column_name='is_v_over',
            where_name='id'),
        is_v_active=True,
        id=bp_id)
    bp_name = await db.get_one(
        await queries.get_value(
            value='name',
            table='best_practice'),
        id=bp_id)
    await callback.bot.send_message(
        chat_id=config.CHANNEL_ID,
        text=f'Голосование за участников Лучшей Практики <b>{bp_name[0]}</b> '
             f'закончилось!')
    await callback.message.answer(
        text='Голосование закончено!',
        reply_markup=keyboards.back)


# обработка нажатиян кнопки получить топ10
async def practice_get_top(message: types.Message, state: FSMContext):
    pass


# обработчка нажатия кнопки предложения
@decorators.error_handler_message
async def make_suggest(message: types.Message, state: FSMContext):
    await message.answer(
        text='Здесь вы можете отправить вашему СитиМенеджеру предложения по '
             'Лучшим Практикам.\n'
             'Напишите и отправьте своё предложение или нажмите "Назад".',
        reply_markup=keyboards.back)
    position = await get_value_by_tgig(
        value='position',
        table='users',
        tg_id=int(message.from_user.id))
    match position:
        case 'mr':
            await UserState.practice_make_suggest_mr.set()
        case 'kas':
            await UserState.practice_make_suggest_kas.set()


# отправка предложения ситименеджеру
@decorators.error_handler_message
async def send_suggest(message: types.Message, state: FSMContext):
    text_to_send = str(message.text)
    user = await get_value_by_tgig(
        value='username',
        table='users',
        tg_id=int(message.from_user.id))
    cm_tg_id = await db.get_one(
        queries.CM_TG_ID,
        int(message.from_user.id))
    if cm_tg_id[0] and int(cm_tg_id[0]) != 0:
        await message.bot.send_message(
            chat_id=int(cm_tg_id[0]),
            text=f'<b>Новое сообщение!</b>\n<u>От:</u>  {user}\n'
                 f'<u>Тема:</u>  Предложения по Лучшим Практикам\n\n'
                 f'{text_to_send}')
        await message.answer(
            text='Ваше предложение отправлено вашему СитиМенеджеру!',
            reply_markup=keyboards.back)
    else:
        await message.answer(
            text='К сожалению ваш СитиМенеджер еще не подключен к боту,'
                 ' вы можете написать ему напрямую.',
            reply_markup=keyboards.back)


# Обработка нажатия инлайн-кнопки под фоткой в канале
async def get_like(callback: types.CallbackQuery, state: FSMContext):
    photo_id = str(callback.data).split('_')[2]
    tg_id = int(callback.from_user.id)
    check_vote = await db.get_one(
        await queries.get_value(
            value='*',
            table='best_practice_vote'),
        tg_id=tg_id,
        photo_id=photo_id,
        is_voted=True)
    if check_vote:
        await callback.answer(text='Вы уже проголосовали за этого участника!',
                              show_alert=False)
    else:
        await db.post(
            queries.VOTE_BP,
            tg_id,
            photo_id,
            True)
        await db.post(
            queries.LIKES_UP,
            photo_id)
        await callback.answer(text='Спасибо, ваш голос учтён!',
                              show_alert=False)


# компануем в обработчик
def register_handlers_best_practice(dp: Dispatcher):
    dp.register_message_handler(
        practice_menu_mr,
        text='Назад↩',
        state=(UserState.practice_menu_mr,
               UserState.practice_make_suggest_mr,
               UserState.practice_take_part_mr_confirm,
               UserState.practice_take_part_mr_photo,
               UserState.practice_take_part_mr_desc))
    dp.register_message_handler(
        practice_menu_kas,
        text='Назад↩',
        state=(UserState.practice_menu_kas,
               UserState.practice_make_suggest_kas,
               UserState.practice_requests_show_kas))
    dp.register_message_handler(
        practice_menu_cm,
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
               UserState.practice_vote_menu_cm,
               UserState.practice_start_voting,
               UserState.practice_stop_voting,
               UserState.practice_top_voting,
               UserState.practice_add,
               UserState.practice_add_desc,
               UserState.practice_add_start,
               UserState.practice_add_stop,
               UserState.practice_add_picture))
    dp.register_message_handler(
        practice_menu_mr,
        text='Практики🗣',
        state=UserState.auth_mr)
    dp.register_message_handler(
        practice_menu_kas,
        text='Практики🗣',
        state=UserState.auth_kas)
    dp.register_message_handler(
        practice_menu_cm,
        text='Практики🗣',
        state=UserState.auth_cm)
    dp.register_message_handler(
        get_current_practice,
        text='Текущие практики🎯',
        state=UserState.practice_menu_mr)
    dp.register_callback_query_handler(
        take_part,
        state=UserState.practice_menu_mr)
    dp.register_callback_query_handler(
        take_part_confirmation,
        state=UserState.practice_take_part_mr_confirm)
    dp.register_message_handler(
        take_part_take_photo,
        content_types=['photo'],
        state=UserState.practice_take_part_mr_photo)
    dp.register_message_handler(
        take_part_take_description,
        state=UserState.practice_take_part_mr_desc)
    dp.register_message_handler(
        manage_practice,
        text='Управлять текущими🔀',
        state=UserState.practice_menu_cm)
    dp.register_callback_query_handler(
        select_action_manage,
        state=UserState.practice_manage_cm)
    dp.register_callback_query_handler(
        action_manage,
        state=UserState.practice_manage_action_cm)
    dp.register_message_handler(
        manage_change_name,
        state=UserState.practice_manage_change_name)
    dp.register_message_handler(
        manage_change_desc,
        state=UserState.practice_manage_change_desc)
    dp.register_message_handler(
        manage_change_pic,
        content_types=['photo'],
        state=UserState.practice_manage_change_pic)
    dp.register_message_handler(
        manage_change_start,
        state=UserState.practice_manage_change_start)
    dp.register_message_handler(
        manage_change_stop,
        state=UserState.practice_manage_change_stop)
    dp.register_message_handler(
        add_new_practice_add_name,
        text='Добавить новую➕',
        state=UserState.practice_menu_cm)
    dp.register_message_handler(
        add_new_practice_add_desc,
        state=UserState.practice_add)
    dp.register_message_handler(
        add_new_practice_add_start,
        state=UserState.practice_add_desc)
    dp.register_message_handler(
        add_new_practice_add_stop,
        state=UserState.practice_add_start)
    dp.register_message_handler(
        add_new_practice_add_picture,
        state=UserState.practice_add_stop)
    dp.register_message_handler(
        add_new_practice,
        content_types=['photo'],
        state=UserState.practice_add_picture)
    dp.register_message_handler(
        practice_requests_kas,
        text='Смотреть заявки📬',
        state=UserState.practice_menu_kas)
    dp.register_callback_query_handler(
        practice_requests_show_kas,
        state=UserState.practice_requests_show_kas)
    dp.register_message_handler(
        practice_requests_cm,
        text='Смотреть заявки📬',
        state=UserState.practice_menu_cm)
    dp.register_callback_query_handler(
        practice_requests_show_cm,
        state=UserState.practice_requests_show_cm)
    dp.register_message_handler(
        make_suggest,
        text='Предложения📝',
        state=(UserState.practice_menu_mr,
               UserState.practice_menu_kas))
    dp.register_message_handler(
        send_suggest,
        state=(UserState.practice_make_suggest_mr,
               UserState.practice_make_suggest_kas))

    dp.register_message_handler(
        practice_vote_menu_cm,
        text='Голосование🗳',
        state=UserState.practice_menu_cm)
    dp.register_message_handler(
        practice_start_voting,
        text='Открыть голосование🟢',
        state=UserState.practice_vote_menu_cm)
    dp.register_callback_query_handler(
        practice_start_voting_send,
        state=UserState.practice_start_voting)
    dp.register_message_handler(
        practice_stop_voting,
        text='Закрыть голосование🛑',
        state=UserState.practice_vote_menu_cm)
    dp.register_callback_query_handler(
        practice_stop_voting_send,
        state=UserState.practice_stop_voting)

    dp.register_callback_query_handler(
        get_like,
        text_startswith='bp_vote_')
