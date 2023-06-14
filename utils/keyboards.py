from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

# кластеры
ZERO_CLUSTER = InlineKeyboardButton('0', callback_data='0')
TWO_CLUSTER = InlineKeyboardButton('2', callback_data='2')

# группируем кластеры в инлайн клаву
CLUSTERS_ALL = InlineKeyboardMarkup().add(ZERO_CLUSTER, TWO_CLUSTER)

# стартовое меню для мерчендайзеров
start_menu_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Инструменты🛠'), KeyboardButton(text='KPI📈')],
    [KeyboardButton(text='Рейтинги📊'), KeyboardButton(text='Кабинет🗄')],
    [KeyboardButton(text='МП🤩'), KeyboardButton(text='Практики🗣')],
    [KeyboardButton(text='Магазин🏦')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')

stuff_menu_merch = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Планограммы🧮'), KeyboardButton(text='ДМП📦')],
    [KeyboardButton(text='Картина Успеха🎉')]],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Выберите команду из меню')


# универсальная кнопка назад
back = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад')]],
                           resize_keyboard=True,
                           one_time_keyboard=True)


# формируем инлайн клавиатуру
def get_list_inline(data):
    get_list_keyboard = InlineKeyboardMarkup()
    for i in data:
        get_list_keyboard.insert(InlineKeyboardButton(f'{i}', callback_data=f'{i}'))
    return get_list_keyboard


# формируем обычную клавиатуру
def get_list_reply(data):
    get_list_keyboard = ReplyKeyboardMarkup()
    for i in data:
        get_list_keyboard.insert(KeyboardButton(f'{i}'))
    return get_list_keyboard
