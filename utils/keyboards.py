from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup

# стартовое меню для мерчендайзеров и KAS
start_menu_mr = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Инструменты🛠'), KeyboardButton(text='KPI📈')],
    [KeyboardButton(text='Рейтинги📊'), KeyboardButton(text='Практики🗣')],
    [KeyboardButton(text='МП🤩'), KeyboardButton(text='Кабинет🗄')],
    [KeyboardButton(text='Магазин🏦')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# стартовое меню для CitiManager
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

# меню рейтингов для мерчендайзера и каса
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
    one_time_keyboard=True
)

# меню практик для каса
practice_menu_kas = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Смотреть заявки📬')],
    [KeyboardButton(text='Предложения📝')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# меню практик для ситименеджера
practice_menu_cm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Управлять текущими🔀')],
    [KeyboardButton(text='Смотреть заявки📬')],
    [KeyboardButton(text='Добавить новую➕')],
    [KeyboardButton(text='Отправить фото в канал⤴')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# меню мотивационных программ
mp_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Текущие МП💸')],
    [KeyboardButton(text='Архив МП🗃')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# меню профиля
profile_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой профиль🗂'),
     KeyboardButton(text='Карьерный рост🔝')],
    [KeyboardButton(text='Кадровые документы🗃'),
     KeyboardButton(text='Опрос💬')],
    [KeyboardButton(text='Выйти из бота🚪')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# меню профиля ситименеджера
profile_menu_cm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой профиль🗂'),
     KeyboardButton(text='Карьерный рост🔝')],
    [KeyboardButton(text='Кадровые документы🗃')],
    [KeyboardButton(text='Выйти из бота🚪')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

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
    InlineKeyboardButton('Да',
                         callback_data='bp_yes'))
confirm_keyboard.insert(
    InlineKeyboardButton('Нет',
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


# формируем инлайн клавиатуру из кортежа
async def get_inline_buttons(data: tuple) -> InlineKeyboardMarkup:
    get_inline_keyboard = InlineKeyboardMarkup()
    for i in data:
        get_inline_keyboard.insert(
            InlineKeyboardButton(f'{i}', callback_data=f'{i}'))
    return get_inline_keyboard
