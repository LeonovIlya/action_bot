import aiofiles
import logging
import re
import time
from aiofiles import os as aios
from aiopath import AsyncPath

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import db
from utils import keyboards, queries
from utils.states import UserState

CLUSTERS = ('0', '2',)
SHOPS = ('Верный', 'Дикси', 'Лента', 'Магнит', 'Перекресток', 'Пятерочка')
MAGNITS = ('Магнит ГМ', 'Магнит МК', 'Магнит ММ')


async def tools_menu(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.tools_menu)
    await UserState.tools_menu.set()


# выбираем кластер
async def planogram_choice(message: types.Message):
    keyboard = await keyboards.get_inline_buttons(CLUSTERS)
    await message.answer(text='Выберите кластер:',
                         reply_markup=keyboard)
    await UserState.tools_plan_cluster.set()


# выбираем торговую сеть
async def cluster_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    await state.update_data(cluster=callback.data)
    keyboard = await keyboards.get_inline_buttons(SHOPS)
    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text='Выберите торговую сеть:',
        reply_markup=keyboard)
    await UserState.tools_plan_shop.set()


# выбираем формат магазина
async def shop_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    if callback.data == 'Магнит':
        keyboard = await keyboards.get_inline_buttons(MAGNITS)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите формат Магнита:',
            reply_markup=keyboard)
    else:
        try:
            data = await db.get_all(queries.NAME_QUERY,
                                    shop_name=str(callback.data))
            data = [i[0] for i in data]
            keyboard = await keyboards.get_inline_buttons(data)
            await callback.bot.edit_message_text(
                chat_id=callback.from_user.id,
                message_id=callback.message.message_id,
                text='Выберите планограмму:',
                reply_markup=keyboard)
            await state.update_data(shop_name=callback.data)
            await UserState.tools_plan_name.set()
        except Exception as error:
            await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                      'Попробуйте еще раз!')
            logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


# формируем запрос к бд, получаем ответ
async def name_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    try:
        name = callback.data
        data = await state.get_data()
        file_link = await db.get_one(
            await queries.get_value(
                value='file_link',
                table='planograms'),
            name=name,
            shop_name=data['shop_name'],
            cluster=data['cluster'])
        print(file_link[0])
        file = AsyncPath(str(file_link[0]))
        if await file.is_file():
            await callback.answer(text='Отправляю файл...',
                                  show_alert=False)
            time.sleep(1)
            async with aiofiles.open(str(file_link[0]), 'rb') as file:
                await callback.message.answer_chat_action(
                    action='upload_document')
                await callback.message.answer_document(file,
                                                       reply_markup=keyboards.back)
        else:
            await callback.message.answer(text='Файл не найден!',
                                          reply_markup=keyboards.back)
    except Exception as error:
        await callback.message.answer(
            text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!',
            reply_markup=keyboards.back)
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def dmp_get(message: types.Message):
    await message.answer(text='Введите 7-и значный номер ТТ:',
                         reply_markup=keyboards.back)
    await UserState.tools_dmp_search.set()


async def dmp_search(message: types.Message):
    tt_num = re.sub(r'\s', '', str(message.text))
    if re.match(r'\d{7}', tt_num) and len(tt_num) == 7:
        try:
            query = await db.get_one(queries.DMP_TT_QUERY,
                                     tt_num=tt_num)
            print(query)
            if query:
                if query[0]:
                    await message.answer(
                        text=f'<b>TT № {tt_num}:</b>\n\n'
                             f'<u>Оборудование:</u>\n'
                             f'{query[0]}\n'
                             f'<u>Выполнение:</u>\n'
                             f'{query[1]:.2%}\n'
                             f'<u>Комментарии:</u>\n'
                             f'{query[2]}',
                        reply_markup=keyboards.back)
                else:
                    await message.answer(text='Информация о ДМП в этой ТТ не '
                                              'найдена!',
                                         reply_markup=keyboards.back)
            else:
                await message.answer(text='❗ ТТ с таким номером не найдена!\n'
                                          'Попробуйте еще раз!',
                                     reply_markup=keyboards.back)
        except Exception as error:
            await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                      'Попробуйте еще раз!')
            logging.info(f'Error: {error}, user: {int(message.from_user.id)}')

    else:
        await message.answer(text='мНомер ТТ не соответствует формату ввода!\n'
                                  'Введите еще раз!',
                             reply_markup=keyboards.back)


async def promo_action(message: types.Message):
    keyboard = await keyboards.get_inline_buttons(SHOPS)
    await message.answer(text='Выберите торговую сеть:',
                         reply_markup=keyboard)
    await UserState.tools_promo.set()


async def get_promo_action(callback: types.CallbackQuery):
    if callback.data == 'Магнит':
        keyboard = await keyboards.get_inline_buttons(MAGNITS)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите формат Магнита:',
            reply_markup=keyboard)
    else:
        try:
            file_link = await db.get_one(
                await queries.get_value(
                    value='file_link',
                    table='promo'),
                shop_name=str(callback.data))
            file = AsyncPath(str(file_link[0]))
            if await file.is_file():
                await callback.answer(text='Отправляю файл...',
                                      show_alert=False)
                time.sleep(1)
                await callback.message.delete()
                await callback.message.answer_chat_action(
                    action='upload_document')
                async with aiofiles.open(str(file_link[0]), 'rb') as file:
                    await callback.message.answer_document(file,
                                                           reply_markup=keyboards.back)
            else:
                await callback.message.answer(text='Файл не найден!',
                                              reply_markup=keyboards.back)
        except Exception as error:
            await callback.message.answer(
                text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!',
                reply_markup=keyboards.back)
            logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


async def picture_success_select(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(
        InlineKeyboardButton('Общая КУ',
                             callback_data='Grocery'))
    keyboard.insert(
        InlineKeyboardButton('КУ косметик',
                             callback_data='Drogerie'))
    await message.answer(text='Выберите Картину Успеха:',
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
            await callback.message.answer(text=f'{i}',
                                          reply_markup=keyboard)
        await UserState.tools_get_ku.set()
    else:
        await callback.message.answer(text='На данный момент нет доступных '
                                           'Картин Успеха!',
                                      reply_markup=keyboards.back)


async def picture_success_send(callback: types.CallbackQuery):
    print(callback.data)
    try:
        file = AsyncPath(f'./files/k_u/{str(callback.data)}')
        if await file.is_file():
            await callback.answer(text='Отправляю файл...',
                                  show_alert=False)
            time.sleep(1)
            await callback.message.delete()
            await callback.message.answer_chat_action(action='upload_document')
            async with aiofiles.open(f'./files/k_u/{str(callback.data)}',
                                     'rb') as file:
                await callback.message.answer_document(file,
                                                       reply_markup=keyboards.back)
        else:
            await callback.message.answer(text='❗ Файл не найден!',
                                          reply_markup=keyboards.back)
    except Exception as error:
        await callback.message.answer(
            text='❗ Кажется что-то пошло не так!\nПопробуйте еще раз!',
            reply_markup=keyboards.back)
        logging.info(f'Error: {error}, user: {int(message.from_user.id)}')


# компануем в обработчик
def register_handlers_tools(dp: Dispatcher):
    dp.register_message_handler(tools_menu,
                                text='Назад↩',
                                state=(UserState.tools_menu,
                                       UserState.tools_promo,
                                       UserState.tools_plan_cluster,
                                       UserState.tools_plan_shop,
                                       UserState.tools_plan_name,
                                       UserState.tools_select_ku,
                                       UserState.tools_get_ku,
                                       UserState.tools_dmp_search))
    dp.register_message_handler(tools_menu,
                                text='Инструменты🛠',
                                state=(UserState.auth_mr,
                                       UserState.auth_kas,
                                       UserState.auth_cm))
    dp.register_message_handler(planogram_choice,
                                text='Планограммы🧮',
                                state=UserState.tools_menu)
    dp.register_message_handler(dmp_get,
                                text='ДМП📦',
                                state=UserState.tools_menu)
    dp.register_message_handler(dmp_search,
                                state=UserState.tools_dmp_search)
    dp.register_message_handler(promo_action,
                                text='Промо🎁',
                                state=UserState.tools_menu)

    dp.register_message_handler(picture_success_select,
                                text='Картина Успеха🎉',
                                state=UserState.tools_menu)
    dp.register_callback_query_handler(picture_success_get,
                                       state=UserState.tools_select_ku)
    dp.register_callback_query_handler(picture_success_send,
                                       state=UserState.tools_get_ku)

    dp.register_callback_query_handler(cluster_choice,
                                       state=UserState.tools_plan_cluster)
    dp.register_callback_query_handler(shop_choice,
                                       state=UserState.tools_plan_shop)
    dp.register_callback_query_handler(name_choice,
                                       state=UserState.tools_plan_name)
    dp.register_callback_query_handler(get_promo_action,
                                       state=UserState.tools_promo)
