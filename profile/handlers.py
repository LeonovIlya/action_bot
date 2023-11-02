import aiofiles
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiopath import AsyncPath

from loader import db
from users.handlers import get_value_by_tgig
from utils import decorators, keyboards, queries
from utils.states import UserState

POSITION = {'mr': 'Мерчендайзер', 'kas': 'Супервайзер', 'cm': 'Ситименеджер'}


async def profile_menu(message: types.Message):
    await message.answer(text="Выберите пункт из меню:",
                         reply_markup=keyboards.profile_menu)
    await UserState.profile_menu.set()


async def profile_menu_cm(message: types.Message):
    await message.answer(text="Выберите пункт из меню:",
                         reply_markup=keyboards.profile_menu_cm)
    await UserState.profile_menu_cm.set()


@decorators.error_handler_message
async def my_profile(message: types.Message, state: FSMContext):
    data = await get_value_by_tgig(
        value='*',
        tg_id=int(message.from_user.id))
    match data[6]:
        case 'mr':
            await message.answer(
                text=f'<b>ФИО:</b> {data[1]}\n'
                     f'<b>Ваш KAS:</b> {data[9]}\n'
                     f'<b>Ваш CM:</b> {data[10]}\n'
                     f'<b>Территория:</b> {data[2]}\n'
                     f'<b>Регион:</b> {data[5]}\n'
                     f'<b>Должность:</b> {POSITION[data[6]]}\n'
                     f'<b>Уровень:</b> {data[7]}\n'
                     f'<b>Баллы:</b> {data[8]}\n',
                reply_markup=keyboards.back)
        case 'kas':
            await message.answer(
                text=f'<b>ФИО:</b> {data[1]}\n'
                     f'<b>Ваш CM:</b> {data[10]}\n'
                     f'<b>Территория:</b> {data[2]}\n'
                     f'<b>Регион:</b> {data[5]}\n'
                     f'<b>Должность:</b> {POSITION[data[6]]}\n'
                     f'<b>Уровень:</b> {data[7]}\n'
                     f'<b>Баллы:</b> {data[8]}\n',
                reply_markup=keyboards.back)
        case 'cm':
            await message.answer(
                text=f'<b>ФИО:</b> {data[1]}\n'
                     f'<b>Территория:</b> {data[2]}\n'
                     f'<b>Регион:</b> {data[5]}\n'
                     f'<b>Должность:</b> {POSITION[data[6]]}\n'
                     f'<b>Уровень:</b> {data[7]}\n'
                     f'<b>Баллы:</b> {data[8]}\n',
                reply_markup=keyboards.back)


@decorators.error_handler_message
async def career(message: types.Message, state: FSMContext):
    path = './files/career/career_growth.pdf'
    file = AsyncPath(path)
    if await file.is_file():
        await message.answer_chat_action(action='upload_document')
        async with aiofiles.open(file, 'rb') as file:
            await message.answer_document(file,
                                          reply_markup=keyboards.back)
    else:
        await message.answer(
            text='❗ Файл не найден!',
            reply_markup=keyboards.back)


async def hr_documents(message: types.Message):
    await message.answer(
        text='Все кадровые вопросы вы можете решить на '
             '<a href="http://infomerch.ru/">едином портале</a>',
        reply_markup=keyboards.back)


async def comments(message: types.Message):
    await message.answer(
        text='Здесь вы можете отправить СитиМенеджеру свой отзыв об '
             'удовлетворённости работой.\nТакже можете оценить работу '
             'данного бота.',
        reply_markup=keyboards.back)
    await UserState.profile_comments.set()


@decorators.error_handler_message
async def send_comments(message: types.Message, state: FSMContext):
    text_to_send = str(message.text)
    user = await get_value_by_tgig(
        value='username',
        tg_id=int(message.from_user.id))
    cm_tg_id = await db.get_one(
        queries.CM_TG_ID,
        int(message.from_user.id))
    if cm_tg_id[0] and int(cm_tg_id[0]) != 0:
        await message.bot.send_message(
            chat_id=cm_tg_id[0],
            text=f'<b>Новое сообщение!</b>\n'
                 f'<u>От:</u>  {user}\n'
                 f'<u>Тема:</u>  Отзыв об удовлетворенности '
                 f'работой/ботом\n\n'
                 f'Текст: {text_to_send}')
        await message.answer(
            text='Ваш отзыв отправлен СитиМенеджеру!',
            reply_markup=keyboards.back)
    else:
        await message.answer(
            text='К сожалению ваш СитиМенеджер еще не подключен к боту, '
                 'вы можете написать ему напрямую.',
            reply_markup=keyboards.back)


@decorators.error_handler_message
async def profile_logout(message: types.Message, state: FSMContext):
    await db.post(
        await queries.update_value(
            table='users',
            column_name='tg_id',
            where_name='tg_id'),
        value='0',
        tg_id=int(message.from_user.id))
    await message.answer(
        text='Вы успешно разлогинились!',
        reply_markup=keyboards.start)
    await state.reset_data()
    await state.finish()


def register_handlers_profile(dp: Dispatcher):
    dp.register_message_handler(
        profile_menu,
        text='Назад↩',
        state=(UserState.profile_menu,
               UserState.profile_comments))
    dp.register_message_handler(
        profile_menu_cm,
        text='Назад↩',
        state=UserState.profile_menu_cm)
    dp.register_message_handler(
        profile_menu,
        text='Кабинет🗄',
        state=(UserState.auth_mr,
               UserState.auth_kas))
    dp.register_message_handler(
        profile_menu_cm,
        text='Кабинет🗄',
        state=UserState.auth_cm)
    dp.register_message_handler(
        profile_logout,
        text='Выйти из бота🚪',
        state=(UserState.profile_menu,
               UserState.profile_menu_cm))
    dp.register_message_handler(
        profile_logout,
        commands=['logout'],
        state='*')
    dp.register_message_handler(
        my_profile,
        text='Мой профиль🗂',
        state=(UserState.profile_menu,
               UserState.profile_menu_cm))
    dp.register_message_handler(
        career,
        text='Карьерный рост🔝',
        state=(UserState.profile_menu,
               UserState.profile_menu_cm))
    dp.register_message_handler(
        hr_documents,
        text='Кадровые документы🗃',
        state=(UserState.profile_menu,
               UserState.profile_menu_cm))
    dp.register_message_handler(
        comments,
        text='Опрос💬',
        state=UserState.profile_menu)
    dp.register_message_handler(
        send_comments,
        state=UserState.profile_comments)
