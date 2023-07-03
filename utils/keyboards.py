from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup

# стартовое меню для мерчендайзеров
start_menu_mr = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Инструменты🛠'), KeyboardButton(text='KPI📈')],
    [KeyboardButton(text='Рейтинги📊'), KeyboardButton(text='Практики🗣')],
    [KeyboardButton(text='МП🤩'), KeyboardButton(text='Кабинет🗄')],
    [KeyboardButton(text='Магазин🏦')]],
    resize_keyboard=True,
    one_time_keyboard=True)
# стартовое меню для KAS
start_menu_kas = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Инструменты🛠'), KeyboardButton(text='KPI📈')],
    [KeyboardButton(text='МП🤩'), KeyboardButton(text='Практики🗣')],
    [KeyboardButton(text='Магазин🏦'), KeyboardButton(text='Кабинет🗄')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# стартовое меню для CitiManager
start_menu_cm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Инструменты🛠'), KeyboardButton(text='KPI📈')],
    [KeyboardButton(text='МП🤩'), KeyboardButton(text='Практики🗣')],
    [KeyboardButton(text='Магазин🏦'), KeyboardButton(text='Кабинет🗄')]],
    resize_keyboard=True,
    one_time_keyboard=True)


tools_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Планограммы🧮'), KeyboardButton(text='ДМП📦')],
    [KeyboardButton(text='Промо🎁'), KeyboardButton(text='Картина Успеха🎉')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)


kpi_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой KPI📈'), KeyboardButton(text='KPI TT🏬')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)


ratings_menu_mr = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои рейтинги📊'),
     KeyboardButton(text='Результаты тестов📋')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)


practice_menu_mr = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Текущие практики🎯')],
    [KeyboardButton(text='Предложения📝')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

practice_menu_kas = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Смотреть заявки📬')],
    [KeyboardButton(text='Предложения📝')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

practice_menu_cm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Управлять текущими🔀')],
    [KeyboardButton(text='Смотреть заявки📬')],
    [KeyboardButton(text='Добавить новую➕')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

profile_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой профиль🗂'),
     KeyboardButton(text='Карьерный рост🔝')],
    [KeyboardButton(text='Кадровые документы🗃'),
     KeyboardButton(text='Опрос💬')],
    [KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

start = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='START▶️')]],
    resize_keyboard=True,
    one_time_keyboard=True)

# универсальная кнопка назад
back = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Назад↩')]],
    resize_keyboard=True,
    one_time_keyboard=True)

main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Главное меню📱')]],
    resize_keyboard=True,
    one_time_keyboard=True)


# формируем инлайн клавиатуру
async def get_inline_buttons(data):
    get_inline_keyboard = InlineKeyboardMarkup()
    for i in data:
        get_inline_keyboard.insert(
            InlineKeyboardButton(f'{i}', callback_data=f'{i}'))
    return get_inline_keyboard
