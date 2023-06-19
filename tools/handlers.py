import logging
import aiofiles
from aiopath import AsyncPath

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState


CLUSTERS = ('0', '2')
SHOPS = ('Верный', 'Дикси', 'Лента', 'Магнит', 'Перекресток', 'Пятерочка')
MAGNITS = ('Магнит ГМ', 'Магнит МК', 'Магнит ММ')


async def tools_menu(message: types.Message):
    await message.answer(text='Выберите пункт из меню:',
                         reply_markup=keyboards.tools_menu_merch)
    await UserState.tools_menu_mr.set()


# выбираем кластер
async def planogram_choice(message: types.Message):
    keyboard = await keyboards.get_inline_buttons(CLUSTERS)
    await message.answer(text='Выберите кластер:',
                         reply_markup=keyboard)
    await UserState.plan_cluster.set()


# выбираем торговую сеть
async def cluster_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(cluster=callback.data)
    keyboard = await keyboards.get_inline_buttons(SHOPS)
    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text='Выберите торговую сеть:',
        reply_markup=keyboard)
    await UserState.plan_shop.set()


# выбираем формат магазина
async def shop_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == 'Магнит':
        keyboard = await keyboards.get_inline_buttons(MAGNITS)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите формат Магнита:',
            reply_markup=keyboard)
    else:
        data = await db.get_stuff_list(queries.name_query,
                                       shop_name=callback.data)
        keyboard = await keyboards.get_inline_buttons(data)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите планограмму:',
            reply_markup=keyboard)
        await state.update_data(shop_name=callback.data)
        await UserState.plan_name.set()


# формируем запрос к бд, получаем ответ
async def name_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()
    name = callback.data
    data = await state.get_data()
    try:
        await callback.message.answer(text='Ожидайте отправки файла...')
        data = await db.get_one(queries.file_query, name=name,
                                shop_name=data['shop_name'],
                                cluster=data['cluster'])
        file = AsyncPath(data)
        if await file.is_file():
            await callback.message.answer(text='Отправляю файл...')
            async with aiofiles.open(data, 'rb') as file:
                await callback.message.answer_document(file,
                                                       reply_markup=keyboards.back)
                await state.finish()
        else:
            await callback.message.answer(text='Файл не найден!',
                                          reply_markup=keyboards.back)
            await state.finish()
    except Exception as error:
        await callback.message.answer(
            text=f'Какая-то ошибка!\nПопробуйте сначала!\nError: {error}',
            reply_markup=keyboards.back)
        await state.finish()
        logging.info('%error', error)


async def get_dmp(message: types.Message, state: FSMContext):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)
    await state.finish()


async def get_picture_success(message: types.Message, state: FSMContext):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)
    await state.finish()


# компануем в обработчик
def register_handlers_planogram(dp: Dispatcher):
    dp.register_message_handler(tools_menu,
                                text='Инструменты🛠')
    dp.register_message_handler(planogram_choice,
                                text='Планограммы🧮',
                                state=UserState.tools_menu_mr)
    dp.register_message_handler(get_dmp,
                                text='ДМП📦',
                                state=UserState.tools_menu_mr)
    dp.register_message_handler(get_picture_success,
                                text='Картина Успеха🎉',
                                state=UserState.tools_menu_mr)
    dp.register_callback_query_handler(cluster_choice,
                                       state=UserState.plan_cluster)
    dp.register_callback_query_handler(shop_choice, state=UserState.plan_shop)
    dp.register_callback_query_handler(name_choice, state=UserState.plan_name)
