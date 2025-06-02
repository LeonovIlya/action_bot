import hashlib

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

import config
from loader import db
from utils import decorators, keyboards, queries
from utils.states import UserState


# клавиатура управления юзерами, проверяем наличие доступа к функции
async def admin_menu(message: types.Message, state: FSMContext):
    if str(message.from_user.id) == str(config.ADMIN_ID):
        await state.reset_data()
        await message.answer(text='Выберите команду:',
                             reply_markup=keyboards.admin_menu)
        await UserState.admin.set()
    else:
        await message.answer(text='У вас нет прав для данной функции!',
                             reply_markup=keyboards.back)


# показывает меню управления пользователями
async def admin_manage_user(message: types.Message):
    await message.answer(text='Выберите команду:',
                         reply_markup=keyboards.manage_user_menu)
    await UserState.admin_manage_user.set()


# добавление нового пользователя, спрашиваем ФИО
async def admin_add_user(message: types.Message):
    await message.answer(text='Введите ФИО полностью:\n'
                              '(Иванов Иван Иванович)',
                         reply_markup=keyboards.back)
    await UserState.admin_add_username.set()


# добавление нового пользователя, спрашиваем территорию
async def admin_add_username(message: types.Message, state: FSMContext):
    username = str(message.text)
    await state.update_data(username=username)
    await message.answer(text='Введите название территории\n'
                              '(Иваново_1)',
                         reply_markup=keyboards.back)
    await UserState.admin_add_ternum.set()


# добавление нового пользователя, проверяем территорию на уникальность,
# спрашиваем пароль
@decorators.error_handler_message
async def admin_add_ternum(message: types.Message, state: FSMContext):
    ter_num = str(message.text)
    check_ter_num = await db.get_one(
        await queries.get_value(
            value='ter_num',
            table='users'),
        username=ter_num)
    if check_ter_num:
        await message.answer(
            text='❗ Такая территория уже есть в базе!\n'
                 'Введите другое название!')
    else:
        await state.update_data(ter_num=ter_num)
        await message.answer(text='Введите пароль пользователя:\n'
                                  '(AbcD1234)',
                             reply_markup=keyboards.back)
        await UserState.admin_add_pwd.set()


# добавление нового пользователя, хэшируем пароль, спрашиваем регион
async def admin_add_pwd(message: types.Message, state: FSMContext):
    pwd = str(message.text)
    password = hashlib.sha512(pwd.encode('utf-8')).hexdigest()
    await state.update_data(pwd=pwd)
    await state.update_data(password=password)
    await message.answer(text='Введите регион пользователя\n'
                              '(Moscow/Center/North)',
                         reply_markup=keyboards.back)
    await UserState.admin_add_region.set()


# добавление нового пользователя, проверяем регион, спрашиваем позицию
async def admin_add_region(message: types.Message, state: FSMContext):
    region = str(message.text)
    if region in ('Moscow', 'Center', 'North'):
        await state.update_data(region=region)
        await message.answer(text='Введите позицию пользователя:\n'
                                  '(mr/kas/cm)',
                             reply_markup=keyboards.back)
        await UserState.admin_add_position.set()
    else:
        await message.answer(text='Кажется вы ошиблись, попробуйте еще раз',
                             reply_markup=keyboards.back)


# добавление нового пользователя, проверяем позицию, спрашиваем грейд
async def admin_add_position(message: types.Message, state: FSMContext):
    position = str(message.text)
    if position in ('mr', 'kas', 'cm'):
        await state.update_data(position=position)
        await message.answer(text='Введите грейд сотрудника:\n'
                                  '(Если нет: "-")',
                             reply_markup=keyboards.back)
        await UserState.admin_add_grade.set()
    else:
        await message.answer(text='Кажется вы ошиблись, попробуйте еще раз',
                             reply_markup=keyboards.back)


# добавление нового пользователя, спрашиваем КАСа из списка текущих в базе
@decorators.error_handler_message
async def admin_add_grade(message: types.Message, state: FSMContext):
    grade = str(message.text)
    await state.update_data(grade=grade)
    data = await state.get_data()
    kas_list = await db.get_all(
        await queries.get_value(
            value='username',
            table='users'),
        region=data['region'],
        position='kas')
    if kas_list:
        text = '\n'.join([i[0] for i in sorted(kas_list)])
        await message.answer(text=f'{text}\n\n'
                                  f'Введите KASа сотрудника из списка выше:',
                             reply_markup=keyboards.back)
        await UserState.admin_add_kas.set()
    else:
        await message.answer(text='хуй',
                             reply_markup=keyboards.back)


# добавление нового пользователя, спрашиваем СМа из списка текущих в базе
@decorators.error_handler_message
async def admin_add_kas(message: types.Message, state: FSMContext):
    kas = str(message.text)
    await state.update_data(kas=kas)
    data = await state.get_data()
    cm_list = await db.get_all(
        await queries.get_value(
            value='username',
            table='users'),
        region=data['region'],
        position='cm')
    text = '\n'.join([i[0] for i in sorted(cm_list)])
    await message.answer(text=f'{text}\n\n'
                              f'Введите CMа сотрудника из списка выше:',
                         reply_markup=keyboards.back)
    await UserState.admin_add_cm.set()


# добавление нового пользователя, добавляем запись в базу
@decorators.error_handler_message
async def admin_add_cm(message: types.Message, state: FSMContext):
    citimanager = str(message.text)
    await state.update_data(citimanager=citimanager)
    data = await state.get_data()
    await db.post(
        queries.INSERT_USER,
        username=data['username'],
        ter_num=data['ter_num'],
        password=data['password'],
        region=data['region'],
        position=data['position'],
        grade=data['grade'],
        kas=data['kas'],
        citimanager=data['citimanager'])
    await message.answer(text=f'Новый пользователь успешно добавлен!\n\n'
                              f'ФИО: {data["username"]}\n'
                              f'Территория: {data["ter_num"]}\n'
                              f'Пароль: {data["pwd"]}',
                         reply_markup=keyboards.back)


# редактирование пользователя, спрашиваем территорию
async def admin_edit_user(message: types.Message):
    await message.answer(text='Введите номер территории:',
                         reply_markup=keyboards.back)
    await UserState.admin_edit_user.set()


# редактирование пользователя, проверяем территорию, спрашиваем данные
@decorators.error_handler_message
async def admin_edit_user_check(message: types.Message, state: FSMContext):
    ter_num = str(message.text)
    check = await db.get_one(
        await queries.get_value(
            value='*',
            table='users'),
        ter_num=ter_num)
    if check:
        await state.update_data(ter_num=ter_num)
        await message.answer(text='Введите данные для изменения в формате:\n'
                                  '{имя_столбца},{данные}\n\n'
                                  'Например: username,Иванов Иван Иванович',
                             reply_markup=keyboards.back)
        await UserState.admin_edit_user_check.set()
    else:
        await message.answer(text='Информация не найдена, попробуйте еще раз!',
                             reply_markup=keyboards.back)


# редактирование пользователя, меняем данные
@decorators.error_handler_message
async def admin_edit_user_set(message: types.Message, state: FSMContext):
    data = str(message.text).split(',')
    state_data = await state.get_data()
    await db.post(
        await queries.update_value(
            table='users',
            column_name=data[0],
            where_name='ter_num'),
        data[1],
        state_data['ter_num'])
    await message.answer(text='Данные успешно обновлены!',
                         reply_markup=keyboards.back)


# информация пользователя из базы по территории, спрашиваем территорию
async def admin_show_info(message: types.Message):
    await message.answer(text='Введите номер территории:',
                         reply_markup=keyboards.back)
    await UserState.admin_show_info.set()


# информация пользователя из базы по территории, проверяем территорию,
# выводим информацию
@decorators.error_handler_message
async def admin_get_info(message: types.Message, state: FSMContext):
    ter_num = str(message.text)
    info = await db.get_one(
        await queries.get_value(
            value='*',
            table='users'),
        ter_num=ter_num)
    if info:
        await message.answer(
            text=f'<b>id:</b> {info[0]}\n'
                 f'<b>username:</b> {info[1]}\n'
                 f'<b>ter_num:</b> {info[2]}\n'
                 f'<b>tg_id:</b> {info[4]}\n'
                 f'<b>region:</b> {info[5]}\n'
                 f'<b>position:</b> {info[6]}\n'
                 f'<b>grade:</b> {info[7]}\n'
                 f'<b>points:</b> {info[8]}\n'
                 f'<b>kas:</b> {info[9]}\n'
                 f'<b>citimanager:</b> {info[10]}\n\n'
                 f'<b>plan_pss:</b> {info[11]:.2%}\n'
                 f'<b>fact_pss:</b> {info[12]:.2%}\n'
                 f'<b>%_pss:</b> {info[13]:.2%}\n'
                 f'<b>plan_osa:</b> {info[14]:.2%}\n'
                 f'<b>fact_osa:</b> {info[15]:.2%}\n'
                 f'<b>%_osa:</b> {info[16]:.2%}\n'
                 f'<b>plan_tt:</b> {info[17]}\n'
                 f'<b>fact_tt:</b> {info[18]}\n'
                 f'<b>%_tt:</b> {info[19]:.2%}\n'
                 f'<b>plan_visits:</b> {info[20]}\n'
                 f'<b>fact_visits:</b> {info[21]}\n'
                 f'<b>%_visits:</b> {info[22]:.2%}\n'
                 f'<b>isa_osa:</b> {info[23]}\n',
            reply_markup=keyboards.back)
    else:
        await message.answer(text='Информация не найдена, попробуйте еще раз!',
                             reply_markup=keyboards.back)


# компануем в обработчик
def register_handlers_admin_manager(dp: Dispatcher):
    dp.register_message_handler(
        admin_menu,
        text='Назад↩',
        state=(UserState.admin,
               UserState.admin_manage_user,
               UserState.admin_add_username,
               UserState.admin_add_ternum,
               UserState.admin_add_pwd,
               UserState.admin_add_region,
               UserState.admin_add_position,
               UserState.admin_add_grade,
               UserState.admin_add_kas,
               UserState.admin_add_cm,
               UserState.admin_edit_user,
               UserState.admin_edit_user_check,
               UserState.admin_show_info))
    dp.register_message_handler(
        admin_menu,
        commands=['admin'],
        state=(UserState.auth_mr,
               UserState.auth_kas,
               UserState.auth_cm))
    dp.register_message_handler(
        admin_manage_user,
        text='Manage Users',
        state=UserState.admin)
    dp.register_message_handler(
        admin_add_user,
        text='Add user',
        state=UserState.admin_manage_user)
    dp.register_message_handler(
        admin_add_username,
        state=UserState.admin_add_username)
    dp.register_message_handler(
        admin_add_ternum,
        state=UserState.admin_add_ternum)
    dp.register_message_handler(
        admin_add_pwd,
        state=UserState.admin_add_pwd)
    dp.register_message_handler(
        admin_add_region,
        state=UserState.admin_add_region)
    dp.register_message_handler(
        admin_add_position,
        state=UserState.admin_add_position)
    dp.register_message_handler(
        admin_add_grade,
        state=UserState.admin_add_grade)
    dp.register_message_handler(
        admin_add_kas,
        state=UserState.admin_add_kas)
    dp.register_message_handler(
        admin_add_cm,
        state=UserState.admin_add_cm)
    dp.register_message_handler(
        admin_edit_user,
        text='Edit user',
        state=UserState.admin_manage_user)
    dp.register_message_handler(
        admin_edit_user_check,
        state=UserState.admin_edit_user)
    dp.register_message_handler(
        admin_edit_user_set,
        state=UserState.admin_edit_user_check)
    dp.register_message_handler(
        admin_show_info,
        text='Show user info',
        state=UserState.admin_manage_user)
    dp.register_message_handler(
        admin_get_info,
        state=UserState.admin_show_info)
