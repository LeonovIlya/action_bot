import asyncio
import re
import logging
import aiofiles

from aiofiles import os as aios
from aiopath import AsyncPath

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import db
from utils import decorators, keyboards, queries
from utils.states import UserState

CLUSTERS = ('0', '1', '2', '3')
SHOPS = ('Верный', 'Дикси', 'Лента', 'Магнит', 'Перекресток', 'Пятерочка')
SHOPS_PROMO = ('Атак', 'Ашан', 'Верный', 'ГиперГлобус', 'Дикси', 'Лента',
               'Магнит', 'Метро', 'Окей', 'Перекресток', 'Пятерочка')
MAGNITS = ('Магнит ГМ', 'Магнит МК', 'Магнит ММ', 'Назад')

R_STR = r'(^\d{6},)|(\w+\sобл,)|(\w+-\w+\sр-н,)|(\w+\sр-н,)|(\w+\sрн,' \
        r')|(\s№\s)|(\sг,)'


async def tools_menu(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer(
        text='Выберите пункт из меню:',
        reply_markup=keyboards.tools_menu)
    await UserState.tools_menu.set()


# выбираем кластер
async def planogram_choice(message: types.Message):
    keyboard = await keyboards.get_inline_buttons(CLUSTERS)
    await message.answer(
        text='Выберите кластер:',
        reply_markup=keyboard)
    await UserState.tools_plan_cluster.set()


# выбираем торговую сеть
async def cluster_choice(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(cluster=callback.data)
    keyboard = await keyboards.get_inline_buttons(SHOPS)
    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text='Выберите торговую сеть:',
        reply_markup=keyboard)
    await UserState.tools_plan_shop.set()


@decorators.error_handler_callback
# выбираем формат магазина
async def shop_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'Назад':
        keyboard = await keyboards.get_inline_buttons(SHOPS)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите торговую сеть:',
            reply_markup=keyboard)
    elif callback.data == 'Магнит':
        keyboard = await keyboards.get_inline_buttons(MAGNITS)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите формат Магнита:',
            reply_markup=keyboard)
    else:
        cluster_data = await state.get_data()
        data = await db.get_all(
            await queries.get_value(
                value='DISTINCT name',
                table='planograms'),
            shop_name=str(callback.data),
            cluster=cluster_data['cluster'])
        if data:
            data = [i[0] for i in data]
            keyboard = await keyboards.get_inline_buttons(data)
            await callback.bot.edit_message_text(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                text='Выберите планограмму:',
                reply_markup=keyboard)
            await state.update_data(shop_name=callback.data)
            await UserState.tools_plan_name.set()
        else:
            await callback.answer(text='Для данного кластера и данной сети нет'
                                       ' планограмм!', show_alert=False)


@decorators.error_handler_callback
# формируем запрос к бд, получаем ответ
async def name_choice(callback: types.CallbackQuery, state: FSMContext):
    name = callback.data
    data = await state.get_data()
    file_link = await db.get_one(
        await queries.get_value(
            value='file_link',
            table='planograms'),
        name=name,
        shop_name=data['shop_name'],
        cluster=data['cluster'])
    try:
        await callback.message.delete()
        file = AsyncPath(str(file_link[0]))
        async with aiofiles.open(file, 'rb') as file:
            await callback.answer(
                text='Отправляю файл...',
                show_alert=False)
            await callback.message.answer_chat_action(
                action='upload_document')
            await callback.message.answer_document(
                file,
                reply_markup=keyboards.back)
    except (TypeError, FileNotFoundError) as error:
        await callback.bot.answer_callback_query(callback.id)
        await callback.message.answer(
            text='Файл не найден!',
            reply_markup=keyboards.back)


async def dmp_get(message: types.Message):
    await message.answer(
        text='Введите 7-и значный номер ТТ:',
        reply_markup=keyboards.back)
    await UserState.tools_dmp_search.set()


@decorators.error_handler_message
async def dmp_search(message: types.Message, state: FSMContext):
    tt_num = re.sub(r'\s', '', str(message.text))
    if re.match(r'\d{7}', tt_num) and len(tt_num) == 7:
        query = await db.get_one(
            await queries.get_value(
                value='*',
                table='tt'),
            tt_num=tt_num)
        if query:
            address = re.sub(R_STR, '', query[4])
            if query[21] or query[22] or query[23]:
                await message.answer(
                    text=f'<b>TT № {tt_num}:</b>\n'
                         f'<b>Сеть:</b> {query[3]}\n'
                         f'<b>Адрес:</b> {address}\n\n'
                         f'<u>Оборудование:</u>\n'
                         f'{query[21]}\n'
                         f'<u>Выполнение:</u>\n'
                         f'{query[22]:.2%}\n'
                         f'<u>Комментарии:</u>\n'
                         f'{query[23]}',
                    reply_markup=keyboards.back)
            else:
                await message.answer(
                    text=f'<b>TT № {tt_num}:</b>\n'
                         f'<b>Сеть:</b> {query[3]}\n'
                         f'<b>Адрес:</b> {address}\n\n'
                         f'❗ Информация о ДМП в этой ТТ не найдена!',
                    reply_markup=keyboards.back)
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


async def promo_action(message: types.Message):
    keyboard = await keyboards.get_inline_buttons(SHOPS_PROMO)
    await message.answer(
        text='Выберите торговую сеть:',
        reply_markup=keyboard)
    await UserState.tools_promo.set()


@decorators.error_handler_callback
async def get_promo_action(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'Магнит':
        keyboard = await keyboards.get_inline_buttons(MAGNITS)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите формат Магнита:',
            reply_markup=keyboard)
    elif callback.data == 'Назад':
        keyboard = await keyboards.get_inline_buttons(SHOPS_PROMO)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите торговую сеть:',
            reply_markup=keyboard)
    else:
        file_link = await db.get_one(
            await queries.get_value(
                value='file_link',
                table='promo'),
            shop_name=str(callback.data))
        file = AsyncPath(str(file_link[0]))
        if await file.is_file():
            await callback.answer(
                text='Отправляю файл...',
                show_alert=False)
            await asyncio.sleep(0.5)
            await callback.message.delete()
            async with aiofiles.open(file, 'rb') as file:
                await callback.message.answer_chat_action(
                    action='upload_document')
                await callback.message.answer_document(
                    file,
                    reply_markup=keyboards.back)
        else:
            await callback.message.answer(
                text='Файл не найден!',
                reply_markup=keyboards.back)


async def picture_success_select(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(
        InlineKeyboardButton('Общая КУ',
                             callback_data='Grocery'))
    keyboard.insert(
        InlineKeyboardButton('КУ косметик',
                             callback_data='Drogerie'))
    await message.answer(
        text='Выберите Картину Успеха:',
        reply_markup=keyboard)
    await UserState.tools_select_ku.set()


async def picture_success_get(callback: types.CallbackQuery):
    ku_list = await aios.listdir(f'./files/k_u/{str(callback.data)}/')
    if ku_list:
        for i in ku_list:
            await callback.message.delete()
            keyboard = InlineKeyboardMarkup()
            keyboard.insert(
                InlineKeyboardButton('Скачать',
                                     callback_data=f'{str(callback.data)}/'
                                                   f'{str(i)}'))
            await callback.message.answer(
                text=f'{i}',
                reply_markup=keyboard)
        await UserState.tools_get_ku.set()
    else:
        await callback.message.answer(
            text='На данный момент нет доступных Картин Успеха!',
            reply_markup=keyboards.back)


@decorators.error_handler_callback
async def picture_success_send(callback: types.CallbackQuery,
                               state: FSMContext):
    file = AsyncPath(f'./files/k_u/{str(callback.data)}')
    if await file.is_file():
        await callback.answer(
            text='Отправляю файл...',
            show_alert=False)
        await asyncio.sleep(0.5)
        await callback.message.delete()
        await callback.message.answer_chat_action(action='upload_document')
        async with aiofiles.open(file, 'rb') as file:
            await callback.message.answer_document(
                file,
                reply_markup=keyboards.back)
    else:
        await callback.message.answer(
            text='❗ Файл не найден!',
            reply_markup=keyboards.back)


# компануем в обработчик
def register_handlers_tools(dp: Dispatcher):
    dp.register_message_handler(
        tools_menu,
        text='Назад↩',
        state=(UserState.tools_menu,
               UserState.tools_promo,
               UserState.tools_plan_cluster,
               UserState.tools_plan_shop,
               UserState.tools_plan_name,
               UserState.tools_select_ku,
               UserState.tools_get_ku,
               UserState.tools_dmp_search))
    dp.register_message_handler(
        tools_menu,
        text='Инструменты🛠',
        state=(UserState.auth_mr,
               UserState.auth_kas,
               UserState.auth_cm))
    dp.register_message_handler(
        planogram_choice,
        text='Планограммы🧮',
        state=UserState.tools_menu)
    dp.register_message_handler(
        dmp_get,
        text='ДМП📦',
        state=UserState.tools_menu)
    dp.register_message_handler(
        dmp_search,
        state=UserState.tools_dmp_search)
    dp.register_message_handler(
        promo_action,
        text='Промо🎁',
        state=UserState.tools_menu)
    dp.register_message_handler(
        picture_success_select,
        text='Картина Успеха🎉',
        state=UserState.tools_menu)
    dp.register_callback_query_handler(
        picture_success_get,
        state=UserState.tools_select_ku)
    dp.register_callback_query_handler(
        picture_success_send,
        state=UserState.tools_get_ku)
    dp.register_callback_query_handler(
        cluster_choice,
        state=UserState.tools_plan_cluster)
    dp.register_callback_query_handler(
        shop_choice,
        state=UserState.tools_plan_shop)
    dp.register_callback_query_handler(
        name_choice,
        state=UserState.tools_plan_name)
    dp.register_callback_query_handler(
        get_promo_action,
        state=UserState.tools_promo)
