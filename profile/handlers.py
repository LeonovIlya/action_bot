from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from loader import db
from utils import keyboards, queries
from utils.states import UserState

POSITION = {'mr': 'Мерчендайзер', 'kas': 'Супервайзер', 'cm': 'Ситименеджер'}


async def profile_menu(message: types.Message):
    await message.answer(text="Выберите пункт из меню:",
                         reply_markup=keyboards.profile_menu)
    await UserState.profile_menu.set()


async def my_profile(message: types.Message):
    try:
        data = await db.get_one(queries.PROFILE,
                                tg_id=int(message.from_user.id))
        match data[3]:
            case 'mr':
                await message.answer(text=''
                                          f'<b>ФИО:</b> {data[0]}\n'
                                          f'<b>Ваш KAS:</b> {data[6]}\n'
                                          f'<b>Ваш CM:</b> {data[7]}\n'
                                          f'<b>Территория:</b> {data[1]}\n'
                                          f'<b>Регион:</b> {data[2]}\n'
                                          f'<b>Должность:</b> {POSITION[data[3]]}\n '
                                          f'<b>Уровень:</b> {data[4]}\n'
                                          f'<b>Баллы:</b> {data[5]}\n',
                                     reply_markup=keyboards.back)
            case 'kas':
                await message.answer(text=''
                                          f'<b>ФИО:</b> {data[0]}\n'
                                          f'<b>Ваш CM:</b> {data[7]}\n'
                                          f'<b>Территория:</b> {data[1]}\n'
                                          f'<b>Регион:</b> {data[2]}\n'
                                          f'<b>Должность:</b> {POSITION[data[3]]}\n'
                                          f'<b>Уровень:</b> {data[4]}\n'
                                          f'<b>Баллы:</b> {data[5]}\n',
                                     reply_markup=keyboards.back)
            case 'cm':
                await message.answer(text=''
                                          f'<b>ФИО:</b> {data[0]}\n'
                                          f'<b>Территория:</b> {data[1]}\n'
                                          f'<b>Регион:</b> {data[2]}\n'
                                          f'<b>Должность:</b> {POSITION[data[3]]}\n'
                                          f'<b>Уровень:</b> {data[4]}\n'
                                          f'<b>Баллы:</b> {data[5]}\n',
                                     reply_markup=keyboards.back)
    except Exception as error:
        await message.answer(text='❗ Кажется что-то пошло не так!\n'
                                  'Попробуйте еще раз!')
        logging.info(
            f'Error: {error}, user: {int(message.from_user.id)}')


async def career(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


async def hr_documents(message: types.Message):
    await message.answer(text='Данная функция в разработке',
                         reply_markup=keyboards.back)


async def poll(message: types.Message):
    pass
    await message.answer(text='')


def register_handlers_profile(dp: Dispatcher):
    dp.register_message_handler(profile_menu,
                                text='Назад↩',
                                state=UserState.profile_menu)

    dp.register_message_handler(profile_menu,
                                text='Кабинет🗄',
                                state=(UserState.auth_mr,
                                       UserState.auth_kas,
                                       UserState.auth_cm))

    dp.register_message_handler(my_profile,
                                text='Мой профиль🗂',
                                state=UserState.profile_menu)
    dp.register_message_handler(career,
                                text='Карьерный рост🔝',
                                state=UserState.profile_menu)
    dp.register_message_handler(hr_documents,
                                text='Кадровые документы🗃',
                                state=UserState.profile_menu)
    dp.register_message_handler(poll,
                                text='Опрос💬',
                                state=UserState.profile_menu)
