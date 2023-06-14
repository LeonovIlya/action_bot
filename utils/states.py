from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    new_user = State()
    auth = State()

    dmp = State()
    dmp_address_search = State()
    dmp_tt_search = State()

    plan_cluster = State()
    plan_shop = State()
    plan_name = State()

    supervisor = State()
    add_merch_set_name = State()
    add_merch_set_password = State()
    edit_merch_set_name = State()
    edit_merch_choice = State()
    edit_merch_set_new_name = State()
    edit_merch_set_new_password = State()
    delete_merch_set_name = State()

    admin = State()
    manage_user = State()
    add_user_set_name = State()
    add_user_set_password = State()
    add_user_set_access_level = State()
    add_user_supervisor_name = State()
    add_user_query = State()

    edit_user_set = State()
    edit_user_choice = State()
    edit_user_set_new_name = State()
    edit_user_set_new_password = State()
    edit_user_set_new_access_level = State()
    edit_user_set_new_supervisor = State()

    delete_user_set_name = State()
