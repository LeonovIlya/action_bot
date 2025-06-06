import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from datetime import datetime as dt

from pprint import pprint

from adaptation.sheets_api import GoogleSheetsProcessor
from adaptation.workdays import add_working_days, parse_date
from loader import db
from utils import decorators, keyboards, queries
from utils.date_validator import is_valid_date
from utils.states import UserState


async def adapt_start_await(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    event, adapt_id, column_name, date_start = callback.data.split(':')[-4:]
    match event:
        case 'await':
            await callback.message.delete()
            new_start_date = await add_working_days(await parse_date(
                date_start), 2)
            await db.post(await queries.update_value(
                table='adaptation',
                column_name=column_name,
                where_name='id'), new_start_date, int(adapt_id))
            await callback.message.answer(text='Ok! Вернемся к этому вопросу через 2 рабочих дня!')
        case 'decline':
            keyboard = await keyboards.get_adapt_decline()
            await callback.message.edit_text(text='Выберите причину отказа:')
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.update_data(adapt_start_id=adapt_id)
        case 'end':
            await callback.message.edit_text(text='Введите дату выхода '
                                                  'сотрудника на работу в '
                                                  'формате *ДД.ММ.ГГГГ*',
                                             parse_mode='MarkdownV2')
            await state.update_data(adapt_start_id=adapt_id)
            await UserState.adapt_start_end.set()


async def adapt_decline_reasons(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    await callback.answer(text='Данные обновляются...', show_alert=False)
    await callback.message.delete()
    data = await state.get_data()
    button_text = str(next(
        btn.text
        for row in callback.message.reply_markup.inline_keyboard
        for btn in row
        if btn.callback_data == callback.data))
    await db.post(
        await queries.update_value(
            table='adaptation',
            column_name=['decline_reason', 'is_archive'],
            where_name='id'),
        button_text, 1,
        data['adapt_start_id'])
    intern_name = await db.get_one(
        await queries.get_value(
            value='intern_name',
            table='adaptation'),
        id=data['adapt_start_id'])
    gsp = GoogleSheetsProcessor()
    await gsp.update_cell_by_name(
        name=intern_name[0],
        column='M',
        value=button_text)
    await callback.message.answer(
        text='Причина отказа сохранена!',
        reply_markup=keyboards.main_menu)




async def adapt_start_end(message: types.Message, state: FSMContext):
    date_1day = await is_valid_date(message.text)
    if date_1day:
        data = await state.get_data()
        await db.post(await queries.update_value('adaptation', 'date_1day',
                                                 'id'), message.text,
                      data['adapt_start_id'])
        intern_name = await db.get_one(
            await queries.get_value(
                value='intern_name',
                table='adaptation'),
            id=data['adapt_start_id'])
        gsp = GoogleSheetsProcessor()
        await gsp.update_cell_by_name(
            name=intern_name[0],
            column='G',
            value=str(message.text))
        await message.answer(text='Дата выхода сотрудника на работу задана!')
    else:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')


# компануем в обработчик
def register_handlers_adaptation(dp: Dispatcher):
    dp.register_callback_query_handler(
        adapt_start_await,
        text_startswith="adapt:start:",
        state='*')
    dp.register_callback_query_handler(
        adapt_decline_reasons,
        text_startswith="adapt:decline:reasons",
        state='*')

    dp.register_message_handler(
        adapt_start_end,
        state=UserState.adapt_start_end)
