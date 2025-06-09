import aiofiles

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiopath import AsyncPath

from adaptation.sheets_api import GoogleSheetsProcessor
from adaptation.workdays import add_working_days, parse_date
from loader import db
from utils import decorators, keyboards, queries
from utils.date_validator import is_valid_date
from utils.states import UserState


@decorators.error_handler_callback
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
            await callback.message.answer(
                text='Ok! Вернемся к этому вопросу через 2 рабочих дня!')
        case 'decline':
            keyboard = await keyboards.get_adapt_decline()
            await callback.message.edit_text(text='Выберите причину отказа:')
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.update_data(adapt_start_id=adapt_id)
            await UserState.adapt_decline.set()
        case 'end':
            await callback.message.edit_text(
                text='Введите дату выхода сотрудника на работу в формате '
                     '*ДД\\.ММ\\.ГГГГ*',
                parse_mode='MarkdownV2')
            await state.update_data(adapt_start_id=adapt_id)
            await UserState.adapt_start_end.set()


@decorators.error_handler_callback
async def adapt_decline_reasons(callback: types.CallbackQuery, state: FSMContext):
    # добавить запрос даты последнего дня работы?

    await callback.answer(text='Данные обновляются...', show_alert=False)
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
    await callback.bot.answer_callback_query(callback.id)
    await callback.message.delete()
    await callback.message.answer(
        text='Причина отказа сохранена!',
        reply_markup=keyboards.main_menu)
    await state.finish()


@decorators.error_handler_message
async def adapt_start_end(message: types.Message, state: FSMContext):
    send_message = await message.answer(text='Данные обновляются...')
    date_1day = await is_valid_date(message.text)
    if date_1day:
        start_date = await parse_date(message.text)
        date_1week, date_3week, date_6week = await add_working_days(
            start_date, [7, 18, 30])
        data = await state.get_data()
        await db.post(
            await queries.update_value(
                table='adaptation',
                column_name=['date_1day', 'date_1week', 'date_3week',
                             'date_6week'],
                where_name='id'),
            message.text, date_1week, date_3week, date_6week, data['adapt_start_id'])
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
        await send_message.edit_text(
            text='Дата выхода сотрудника на работу задана!\n Не забудь про '
                 'план адаптации! и помни, новичку нужно внимание и опытный '
                 'наставник!')
        file = AsyncPath('./files/adaptation/test.txt')
        if await file.is_file():
            await message.answer_chat_action(action='upload_document')
            async with aiofiles.open(file, 'rb') as file:
                await message.answer_document(
                    file,
                    reply_markup=keyboards.main_menu)
        await state.finish()
    else:
        await message.answer(text='❗ Неверный ввод, попробуйте еще раз!')


@decorators.error_handler_callback
async def adapt_1week(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    event, adapt_id = callback.data.split(':')[-2:]
    match event:
        case 'go':
            await callback.message.delete()
            await callback.message.answer(
                text='Отлично! Давай еще раз вспомним про план адаптации!')
            file = AsyncPath('./files/adaptation/test.txt')
            if await file.is_file():
                await callback.message.answer_chat_action(action='upload_document')
                async with aiofiles.open(file, 'rb') as file:
                    await callback.message.answer_document(
                        file,
                        reply_markup=keyboards.main_menu)
            await state.finish()
        case 'decline':
            keyboard = await keyboards.get_adapt_decline()
            await callback.message.edit_text(text='Выберите причину отказа:')
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.update_data(adapt_start_id=adapt_id)
            await UserState.adapt_decline.set()


@decorators.error_handler_callback
async def adapt_3week(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    event, adapt_id = callback.data.split(':')[-2:]
    match event:
        case 'go':
            await callback.message.delete()
        case 'decline':
            keyboard = await keyboards.get_adapt_decline()
            await callback.message.edit_text(text='Выберите причину отказа:')
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.update_data(adapt_start_id=adapt_id)
            await UserState.adapt_decline.set()


@decorators.error_handler_callback
async def adapt_3week_5(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    event, adapt_id = callback.data.split(':')[-2:]
    match event:
        case 'yes':
            await callback.message.delete()
            await callback.message.answer(
                text='Отлично! Детально изучить ответы можно запросив их у '
                     'твоего HR Partner!')
        case 'decline':
            keyboard = await keyboards.get_adapt_decline()
            await callback.message.edit_text(text='Выберите причину отказа:')
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.update_data(adapt_start_id=adapt_id)
            await UserState.adapt_decline.set()


@decorators.error_handler_callback
async def adapt_6week(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    event, adapt_id = callback.data.split(':')[-2:]
    match event:
        case 'go':
            await callback.message.delete()
            await callback.message.answer(
                text='Отлично! Успешный процесс адаптации - результат хорошей работы руководителя. Ты молодец! Желаю и дальше удачи с новичками!')
        case 'decline':
            keyboard = await keyboards.get_adapt_decline()
            await callback.message.edit_text(text='Выберите причину отказа:')
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.update_data(adapt_start_id=adapt_id)
            await UserState.adapt_decline.set()


@decorators.error_handler_callback
async def adapt_6week_3(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.answer_callback_query(callback.id)
    event, adapt_id = callback.data.split(':')[-2:]
    match event:
        case 'yes':
            await callback.message.delete()
            await callback.message.answer(
                text='Отлично!')
        case 'forgot':
            await callback.message.delete()
            await callback.message.answer(
                text='Поторопись!')


# компануем в обработчик
def register_handlers_adaptation(dp: Dispatcher):
    dp.register_callback_query_handler(
        adapt_start_await,
        text_startswith="adapt:start:",
        state='*')
    dp.register_callback_query_handler(
        adapt_1week,
        text_startswith="adapt:1week:",
        state='*')
    dp.register_callback_query_handler(
        adapt_3week,
        text_startswith="adapt:3week:",
        state='*')
    dp.register_callback_query_handler(
        adapt_3week_5,
        text_startswith="adapt:3week_5:",
        state='*')
    dp.register_callback_query_handler(
        adapt_6week,
        text_startswith="adapt:6week:",
        state='*')
    dp.register_callback_query_handler(
        adapt_6week_3,
        text_startswith="adapt:6week_3:",
        state='*')
    dp.register_callback_query_handler(
        adapt_decline_reasons,
        text_startswith="adapt:decline:reasons",
        state=UserState.adapt_decline)
    dp.register_message_handler(
        adapt_start_end,
        state=UserState.adapt_start_end)
