NAME_QUERY = "SELECT DISTINCT name FROM planograms"

BP_NAME = "SELECT name, desc, datetime_start, datetime_stop, pics FROM "\
          "best_practice"

MAX_ID = "SELECT MAX(id) FROM best_practice"

INSERT_PRACTICE_MR = "INSERT INTO best_practice_mr (best_practice, username, "\
                  "datetime_added, pics) VALUES (?, ?, ?, ?)"

INSERT_PRACTICE = "INSERT INTO best_practice (name, desc, user_added, "\
                  "datetime_added, datetime_start, datetime_stop, is_active, "\
                  "pics) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "

UPDATE_TG_ID = "UPDATE users SET tg_id = ? WHERE ter_num = ?"
LOGOUT = "UPDATE users SET tg_id = NULL WHERE tg_id = ?"

KP_MR_QUERY = "SELECT plan_pss, fact_pss, [%_pss], plan_osa, fact_osa, "\
               "[%_osa], plan_tt, fact_tt, [%_tt], plan_visits, fact_visits,"\
               "[%_visits] FROM users"

KPI_TT_QUERY = "SELECT address, mr, kas, plan_pss, fact_pss, [%_pss], "\
               "plan_osa, fact_osa, [%_osa], plan_tt, fact_tt, [%_tt], "\
               "FROM tt"


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
