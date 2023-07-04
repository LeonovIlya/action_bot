NAME_QUERY = "SELECT DISTINCT name FROM planograms"

BP_NAME = "SELECT name, desc, datetime_start, datetime_stop, file_link FROM "\
          "best_practice"

MAX_ID = "SELECT MAX(id) FROM best_practice"

INSERT_PRACTICE_MR = "INSERT INTO best_practice_mr (best_practice, username, "\
                     "tg_id, datetime_added, desc, file_link, kas_checked, "\
                     "kas_approved, cm_checked, cm_approved, active) "\
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

INSERT_PRACTICE = "INSERT INTO best_practice (region, name, desc, "\
                  "user_added, datetime_added, datetime_start, datetime_stop,"\
                  " is_active, over, file_link) "\
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "

UPDATE_TG_ID = "UPDATE users SET tg_id = ? WHERE ter_num = ?"
LOGOUT = "UPDATE users SET tg_id = NULL WHERE tg_id = ?"

KP_MR_QUERY = "SELECT plan_pss, fact_pss, [%_pss], plan_osa, fact_osa, "\
              "[%_osa], plan_tt, fact_tt, [%_tt], plan_visits, fact_visits,"\
              "[%_visits] FROM users"

KPI_TT_QUERY = "SELECT address, mr, kas, plan_pss, fact_pss, [%_pss], "\
               "plan_osa, fact_osa, [%_osa], plan_tt, fact_tt, [%_tt] "\
               "FROM tt"
DMP_TT_QUERY = "SELECT dmp_text, [%_dmp], dmp_comm FROM tt"

BP_PHOTOS = "SELECT id, tg_id, desc, file_link from best_practice_mr"

BP_KAS = "UPDATE best_practice_mr SET kas_checked = ?, kas_approved = ? "\
         "WHERE id = ?"
BP_CM = "UPDATE best_practice_mr SET cm_checked = ?, cm_approved = ? "\
        "WHERE id = ?"

PROFILE = "SELECT username, ter_num, region, position, grade, points, kas, "\
          "citimanager FROM users"


async def get_value(value: str, table: str) -> str:
    return f"SELECT {value} FROM {table}"


async def ratings_query_all(column_name: str) -> str:
    return f"SELECT rank FROM ( SELECT *, ROW_NUMBER() OVER ("\
           f"ORDER BY {column_name} DESC NULLS LAST) AS rank FROM users)"


async def ratings_query(column_name: str,
                        where_name: str,
                        where_value: str) -> str:
    return f"SELECT rank FROM"\
           f"(SELECT *, ROW_NUMBER() OVER"\
           f"(ORDER BY {column_name} DESC NULLS LAST)"\
           f"AS rank FROM users WHERE {where_name} = '{where_value}')"
