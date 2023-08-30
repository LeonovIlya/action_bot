from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    start_auth_get_login = State()
    start_auth_get_password = State()

    admin = State()
    admin_manage_user = State()
    admin_add_username = State()
    admin_add_ternum = State()
    admin_add_pwd = State()
    admin_add_region = State()
    admin_add_position = State()
    admin_add_grade = State()
    admin_add_kas = State()
    admin_add_cm = State()
    admin_edit_user = State()
    admin_edit_user_check = State()
    admin_show_info = State()

    auth_mr = State()
    auth_kas = State()
    auth_cm = State()

    tools_menu = State()

    tools_dmp = State()
    tools_dmp_tt_search = State()

    tools_plan_cluster = State()
    tools_plan_shop = State()
    tools_plan_name = State()

    tools_promo = State()

    tools_select_ku = State()
    tools_get_ku = State()

    tools_dmp_search = State()

    kpi_menu = State()
    kpi_search_tt = State()

    mp_menu = State()

    practice_menu_mr = State()
    practice_menu_kas = State()
    practice_menu_cm = State()

    practice_manage_cm = State()
    practice_manage_action_cm = State()
    practice_manage_change_name = State()
    practice_manage_change_desc = State()
    practice_manage_change_pic = State()
    practice_manage_change_start = State()
    practice_manage_change_stop = State()

    practice_take_part_mr = State()
    practice_take_part_mr_confirm = State()
    practice_take_part_mr_photo = State()
    practice_take_part_mr_desc = State()

    practice_add = State()
    practice_add_desc = State()
    practice_add_start = State()
    practice_add_stop = State()
    practice_add_picture = State()

    practice_requests_show_kas = State()
    practice_requests_show_cm = State()

    practice_vote_menu_cm = State()
    practice_start_voting = State()
    practice_stop_voting = State()
    practice_top_voting = State()

    practice_make_suggest_mr = State()
    practice_make_suggest_kas = State()

    practice_voting = State()

    ratings_menu_mr = State()

    profile_menu = State()
    profile_menu_cm = State()
    profile_comments = State()
