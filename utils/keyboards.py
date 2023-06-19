from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup

# стартовое меню для мерчендайзеров
start_menu_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Инструменты🛠'), KeyboardButton(text='KPI📈')],
    [KeyboardButton(text='Рейтинги📊'), KeyboardButton(text='Кабинет🗄')],
    [KeyboardButton(text='МП🤩'), KeyboardButton(text='Практики🗣')],
    [KeyboardButton(text='Магазин🏦')]],
    resize_keyboard=True,
    one_time_keyboard=True)

tools_menu_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Планограммы🧮'), KeyboardButton(text='ДМП📦')],
    [KeyboardButton(text='Картина Успеха🎉')]],
    resize_keyboard=True,
    one_time_keyboard=True)

kpi_menu_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мой KPI📈'), KeyboardButton(text='KPI TT🏬')]],
    resize_keyboard=True,
    one_time_keyboard=True)

ratings_menu_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Мои рейтинги📊'),
     KeyboardButton(text='Результаты тестов📋')]],
    resize_keyboard=True,
    one_time_keyboard=True)

practice_menu_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Текущие практики🎯')],
    [KeyboardButton(text='Участвовать📸')],
    [KeyboardButton(text='Предложения📝')]
])

practice_menu_citimanager = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Управлять текущими')],
    [KeyboardButton(text='Добавить новую')]
])

# универсальная кнопка назад
back = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад')]],
                           resize_keyboard=True,
                           one_time_keyboard=True)


# формируем инлайн клавиатуру
async def get_inline_buttons(data):
    get_inline_keyboard = InlineKeyboardMarkup()
    for i in data:
        get_inline_keyboard.insert(
            InlineKeyboardButton(f'{i}', callback_data=f'{i}'))
    return get_inline_keyboard
