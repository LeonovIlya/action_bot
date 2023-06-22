from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    start_auth_get_login = State()
    start_auth_get_password = State()

    auth_mr = State()
    auth_kas = State()
    auth_citimanager = State()

    tools_menu_mr = State()

    dmp = State()
    dmp_address_search = State()
    dmp_tt_search = State()

    plan_cluster = State()
    plan_shop = State()
    plan_name = State()

    kpi_menu_mr = State()

    practice_menu_mr = State()
    practice_menu_citimanager = State()

    practice_take_part_mr = State()
    practice_take_part_mr_confirm = State()

    practice_add = State()
    practice_add_desc = State()
    practice_add_start = State()
    practice_add_stop = State()
    practice_add_picture = State()

    ratings_menu_mr = State()
