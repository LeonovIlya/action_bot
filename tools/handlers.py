import aiofiles
import logging
import time
from aiopath import AsyncPath

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState

CLUSTERS = ('0', '2', '3')
SHOPS = ('Верный', 'Дикси', 'Лента', 'Магнит', 'Перекресток', 'Пятерочка')
MAGNITS = ('Магнит ГМ', 'Магнит МК', 'Магнит ММ')


async def tools_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.tools_menu_merch)
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
            await message.answer(text='Кажется что-то пошло не так!\n'
                                      'Попробуйте еще раз!')
            logging.info(
                f'DB error: {error}, user: {int(message.from_user.id)}')


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
        file = AsyncPath(str(file_link[0]))
        if await file.is_file():
            await callback.answer(text='Отправляю файл...',
                                  show_alert=False)
            time.sleep(1)
            async with aiofiles.open(str(file_link[0]), 'rb') as file:
                await callback.message.answer_document(file,
                                                       reply_markup=keyboards.back)
                await UserState.tools_menu.set()
        else:
            await callback.message.answer(text='Файл не найден!',
                                          reply_markup=keyboards.back)
            await UserState.tools_menu.set()
    except Exception as error:
        await callback.message.answer(
            text=f'Какая-то ошибка!\nПопробуйте сначала!\nError: {error}',
            reply_markup=keyboards.back)
        await UserState.tools_menu.set()
        logging.info('%error', error)


async def get_dmp(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


async def promo_action(message: types.Message):
    keyboard = await keyboards.get_inline_buttons(SHOPS)
    await message.answer(text='Выберите торговую сеть:',
                         reply_markup=keyboard)
    await UserState.tools_promo.set()


async def get_promo_action(callback: types.CallbackQuery):
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
            await callback.message.delete()
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
                async with aiofiles.open(str(file_link[0]), 'rb') as file:
                    await callback.message.answer_document(file,
                                                           reply_markup=keyboards.back)
                    await UserState.tools_menu.set()
            else:
                await callback.message.answer(text='Файл не найден!',
                                              reply_markup=keyboards.back)
                await UserState.tools_menu.set()
        except Exception as error:
            await callback.message.answer(
                text=f'Какая-то ошибка!\nПопробуйте сначала!\nError: {error}',
                reply_markup=keyboards.back)
            await UserState.tools_menu.set()
            logging.info('%error', error)


async def get_picture_success(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


# компануем в обработчик
def register_handlers_tools(dp: Dispatcher):
    dp.register_message_handler(tools_menu,
                                text='Назад↩',
                                state=(UserState.tools_menu,
                                       UserState.tools_promo,
                                       UserState.tools_plan_cluster,
                                       UserState.tools_plan_shop,
                                       UserState.tools_plan_name))
    dp.register_message_handler(tools_menu,
                                text='Инструменты🛠',
                                state=[UserState.auth_mr,
                                       UserState.auth_kas,
                                       UserState.auth_citimanager])
    dp.register_message_handler(planogram_choice,
                                text='Планограммы🧮',
                                state=UserState.tools_menu)
    dp.register_message_handler(get_dmp,
                                text='ДМП📦',
                                state=UserState.tools_menu)
    dp.register_message_handler(promo_action,
                                text='Промо🎁',
                                state=UserState.tools_menu)
    dp.register_message_handler(get_picture_success,
                                text='Картина Успеха🎉',
                                state=UserState.tools_menu)
    dp.register_callback_query_handler(cluster_choice,
                                       state=UserState.tools_plan_cluster)
    dp.register_callback_query_handler(shop_choice,
                                       state=UserState.tools_plan_shop)
    dp.register_callback_query_handler(name_choice,
                                       state=UserState.tools_plan_name)
    dp.register_callback_query_handler(get_promo_action,
                                       state=UserState.tools_promo)
