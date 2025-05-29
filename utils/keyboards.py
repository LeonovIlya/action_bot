from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup


# стартовое меню для админ-функций
admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Manage Users')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню управления пользователями
manage_user_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Add user'), KeyboardButton(text='Edit user')],
    [KeyboardButton(text='Show user info')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# стартовое меню для мерчендайзеров и супервайзера
start_menu_mr = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Инструменты🛠'), KeyboardButton(text='KPI📈')],
    [KeyboardButton(text='Рейтинги📊'), KeyboardButton(text='Практики🗣')],
    [KeyboardButton(text='МП🤩'), KeyboardButton(text='Кабинет🗄')],
    [KeyboardButton(text='Магазин🏦')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# стартовое меню для ситименеджера
start_menu_cm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Инструменты🛠'), KeyboardButton(text='KPI📈')],
    [KeyboardButton(text='МП🤩'), KeyboardButton(text='Практики🗣')],
    [KeyboardButton(text='Магазин🏦'), KeyboardButton(text='Кабинет🗄')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню инструменты
tools_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Планограммы🧮'), KeyboardButton(text='ДМП📦')],
    [KeyboardButton(text='Промо🎁'), KeyboardButton(text='Картина Успеха🎉')],
    [KeyboardButton(text='Калькулятор PSS🔢')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню kpi
kpi_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой KPI📈'), KeyboardButton(text='KPI TT🏬')],
    [KeyboardButton(text='Информация по бонусу💰')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню рейтингов для мерчендайзера и супервайзера
ratings_menu_mr = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои рейтинги📊'),
     KeyboardButton(text='Результаты тестов📋')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню практик для мерчендайзера
practice_menu_mr = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Текущие практики🎯')],
    [KeyboardButton(text='Предложения📝')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню практик для супервайзера
practice_menu_kas = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Смотреть заявки📬')],
    [KeyboardButton(text='Предложения📝')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню практик для ситименеджера
practice_menu_cm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Управлять текущими🔀')],
    [KeyboardButton(text='Смотреть заявки📬')],
    [KeyboardButton(text='Добавить новую➕')],
    [KeyboardButton(text='Голосование🗳')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню голосований ситименеджера
vote_menu_cm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Получить ТОП-10🔟')],
    [KeyboardButton(text='Отправить в архив🗃')],
    [KeyboardButton(text='Назад↩')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню мотивационных программ
mp_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Текущие МП💸')],
    [KeyboardButton(text='Архив МП🗃')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню профиля
profile_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой профиль🗂'),
     KeyboardButton(text='Карьерный рост🔝')],
    [KeyboardButton(text='Кадровые документы🗃'),
     KeyboardButton(text='Опрос💬')],
    [KeyboardButton(text='Выйти из бота🚪')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню профиля ситименеджера
profile_menu_cm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой профиль🗂'),
     KeyboardButton(text='Карьерный рост🔝')],
    [KeyboardButton(text='Кадровые документы🗃')],
    [KeyboardButton(text='Выйти из бота🚪')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# меню карьерного роста
career_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Истории успеха🏆'),
     KeyboardButton(text='Карьерная карта📋')],
    [KeyboardButton(text='Назад↩')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# стартовая кнопка
start = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='START▶️')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# универсальная кнопка назад
back = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Назад↩')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# универсальная кнопка главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# инлайн клавиатура да/нет
confirm_keyboard = InlineKeyboardMarkup()
confirm_keyboard.insert(
    InlineKeyboardButton('Да✅',
                         callback_data='bp_yes'))
confirm_keyboard.insert(
    InlineKeyboardButton('Нет❌',
                         callback_data='bp_no'))

# инлайн клавиатура редактирования лучших практик
manage_keyboard = InlineKeyboardMarkup()
manage_keyboard.add(
    InlineKeyboardButton('Изменить название',
                         callback_data='change_name'))
manage_keyboard.add(
    InlineKeyboardButton('Изменить описание',
                         callback_data='change_desc'))
manage_keyboard.add(
    InlineKeyboardButton('Изменить картинку',
                         callback_data='change_pic'))
manage_keyboard.add(
    InlineKeyboardButton('Изменить дату начала',
                         callback_data='change_start'))
manage_keyboard.add(
    InlineKeyboardButton('Изменить дату окончания',
                         callback_data='change_stop'))
manage_keyboard.add(
    InlineKeyboardButton('Удалить практику',
                         callback_data='delete_bp'))

# инлайн клавиатура модерации
accept_keyboard = InlineKeyboardMarkup()
accept_keyboard.insert(
    InlineKeyboardButton('Принять✅',
                         callback_data='Accept'))
accept_keyboard.insert(
    InlineKeyboardButton('Отклонить❌',
                         callback_data='Decline'))

# инлайн клавиатура калькулятора PSS
pss_calc_keyboard = InlineKeyboardMarkup()
pss_calc_keyboard.row(
    InlineKeyboardButton('Whiskas ПАУЧ',
                         callback_data='pss_calc_1'),
    InlineKeyboardButton('Perfect Fit ПАУЧ',
                         callback_data='pss_calc_2'))
pss_calc_keyboard.add(
    InlineKeyboardButton('Sheba ПАУЧ',
                         callback_data='pss_calc_3'))
pss_calc_keyboard.row(
    InlineKeyboardButton('Whiskas СУХОЙ',
                         callback_data='pss_calc_3'),
    InlineKeyboardButton('Perfect Fit СУХОЙ',
                         callback_data='pss_calc_1'))

# инлайн клавиатура адаптации, стартовая дата
adapt_start = InlineKeyboardMarkup()
adapt_start.row(
    InlineKeyboardButton(
        'Он еще проходит стажировку.',
        callback_data='adapt_start_await'))
adapt_start.row(
    InlineKeyboardButton(
        'Кандидат отказался от вакансии.',
        callback_data='adapt_start_decline'))
adapt_start.row(InlineKeyboardButton(
    'Прошел стажировку, выходит на работу.',
    callback_data='adapt_start_done'))


class AsyncAdaptationKeyboards:
    @staticmethod
    async def get_adapt_start(record_id: int) -> InlineKeyboardMarkup:
        """Асинхронная генерация клавиатуры с валидацией"""
        if not isinstance(record_id, int) or record_id <= 0:
            raise ValueError("Invalid record ID")

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                        text='Он еще проходит стажировку.',
                        callback_data=f'adapt_start_await_{record_id}')],
                [InlineKeyboardButton(
                        text='Кандидат отказался от вакансии.',
                        callback_data=f'adapt_start_decline_{record_id}')],
                [InlineKeyboardButton(
                        text='Прошел стажировку, выходит на работу.',
                        callback_data=f'adapt_start_decline_{record_id}')]])



# формируем инлайн клавиатуру из кортежа
async def get_inline_buttons(data: tuple | list) -> InlineKeyboardMarkup:
    get_inline_keyboard = InlineKeyboardMarkup()
    for i in sorted(data):
        get_inline_keyboard.insert(
            InlineKeyboardButton(f'{i}', callback_data=f'{i}'))
    return get_inline_keyboard
