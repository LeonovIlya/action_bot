from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    new_user = State()
    auth_user = State()

    tools_menu = State()

    dmp = State()
    dmp_address_search = State()
    dmp_tt_search = State()

    plan_cluster = State()
    plan_shop = State()
    plan_name = State()

    kpi_menu = State()

    ratings_menu = State()
