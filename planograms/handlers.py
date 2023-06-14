import logging
from pathlib import Path

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState


# выбираем кластер
async def planogram_choice(message: types.Message):
    await message.answer(text='Выберите кластер:',
                         reply_markup=keyboards.CLUSTERS_ALL)
    await UserState.plan_cluster.set()


# выбираем торговую сеть
async def cluster_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(cluster=callback.data)
    data = await db.get_stuff_list(queries.shop_list)
    await callback.bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text='Выберите торговую сеть:',
        reply_markup=keyboards.get_list_inline(data))
    await UserState.plan_shop.set()


# выбираем формат магазина
async def shop_choice(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == 'Магнит':
        data = await db.get_stuff_list(queries.magnit_list,
                                       chain_name=callback.data)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите формат Магнита:',
            reply_markup=keyboards.get_list_inline(
                data))

    elif callback.data == 'Магнит ММ':
        data = await db.get_stuff_list(queries.name_query,
                                       shop_name=callback.data)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id,
            text='Выберите планограмму:',
            reply_markup=keyboards.get_list_inline(
                data))
        await state.update_data(shop_name=callback.data)
        await UserState.plan_name.set()

    elif callback.data == 'Магнит ГМ':
        data = await db.get_stuff_list(queries.name_query,
                                       shop_name=callback.data)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id, text='Выберите '
                                                         'планограмму:',
            reply_markup=keyboards.get_list_inline(
                data))
        await state.update_data(shop_name=callback.data)
        await UserState.plan_name.set()

    elif callback.data == 'Магнит МК':
        data = await db.get_stuff_list(queries.name_query,
                                       shop_name=callback.data)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id, text='Выберите '
                                                         'планограмму:',
            reply_markup=keyboards.get_list_inline(
                data))
        await state.update_data(shop_name=callback.data)
        await UserState.plan_name.set()
    else:
        data = await db.get_stuff_list(queries.name_query,
                                       shop_name=callback.data)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            message_id=callback.message.message_id, text='Выберите '
                                                         'планограмму:',
            reply_markup=keyboards.get_list_inline(
                data))
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
        data = await db.get_stuff(queries.file_query, name=name,
                                  shop_name=data['shop_name'],
                                  cluster=data['cluster'])
        file = Path(data)
        if file.is_file():
            await callback.message.answer(text='Отправляю файл...')
            with open(data, 'rb') as file:
                await callback.message.answer_document(file,
                                                       reply_markup=keyboards.back)
                await state.finish()
        else:
            await callback.message.answer(text='Файл не найден!',
                                          reply_markup=keyboards.back)
            await state.finish()
    except Exception as error:
        await callback.message.answer(
            text='Какая-то ошибка!\nПопробуйте сначала!\nError: %s' % error,
            reply_markup=keyboards.back)
        await state.finish()
        logging.info(f'{error}')


# компануем в обработчик
def register_handlers_planogram(dp: Dispatcher):
    dp.register_message_handler(planogram_choice, text='Планограммы🧮')
    dp.register_callback_query_handler(cluster_choice,
                                       state=UserState.plan_cluster)
    dp.register_callback_query_handler(shop_choice, state=UserState.plan_shop)
    dp.register_callback_query_handler(name_choice, state=UserState.plan_name)
