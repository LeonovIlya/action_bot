NAME_QUERY = "SELECT DISTINCT name FROM planograms"

BP_NAME = "SELECT name, desc, datetime_start, datetime_stop, file_link FROM " \
          "best_practice"

INSERT_USER = "INSERT INTO users (username, ter_num, password, region, "\
              "position, grade, kas, citimanager) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

INSERT_PRACTICE_MR = "INSERT INTO best_practice_mr (best_practice, username, "\
                     "kas, tg_id, datetime_added, desc, file_link, " \
                     "kas_checked, kas_approved, cm_checked, cm_approved," \
                     " active, posted) " \
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

INSERT_PRACTICE = "INSERT INTO best_practice (region, name, desc, " \
                  "user_added, datetime_added, datetime_start, datetime_stop,"\
                  " is_active, over, file_link) " \
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "

KP_MR_QUERY = "SELECT plan_pss, fact_pss, [%_pss], plan_osa, fact_osa, " \
              "[%_osa], plan_tt, fact_tt, [%_tt], plan_visits, fact_visits," \
              "[%_visits], isa_osa FROM users"

KPI_TT_QUERY = "SELECT address, chain, mr, kas, plan_pss, fact_pss, [%_pss], "\
               "plan_osa, fact_osa, [%_osa], plan_tt, fact_tt, [%_tt], " \
               "plan_visits, fact_visits, [%_visits], isa_osa FROM tt"
DMP_TT_QUERY = "SELECT chain, address, dmp_text, [%_dmp], dmp_comm FROM tt"

BP_PHOTOS = "SELECT id, username, tg_id, desc, file_link from " \
            "best_practice_mr"

BP_KAS = "UPDATE best_practice_mr SET kas_checked = ?, kas_approved = ? " \
         "WHERE id = ?"
BP_CM = "UPDATE best_practice_mr SET cm_checked = ?, cm_approved = ?, " \
        "active = ? WHERE id = ?"

PROFILE = "SELECT username, ter_num, region, position, grade, points, kas, " \
          "citimanager FROM users"

DELETE_BP = "DELETE FROM best_practice WHERE name = ?"

DELETE_BP_MR = "DELETE FROM best_practice_mr WHERE id = ?"


async def update_value(table: str, column_name: str, where_name: str) -> str:
    return f"UPDATE {table} SET {column_name} = ? WHERE {where_name} = ?"


async def count(scope: str) -> str:
    return f"SELECT COUNT(*) FROM users WHERE {scope} = ?"


async def get_value(value: str, table: str) -> str:
    return f"SELECT {value} FROM {table}"


async def ratings_query_all(column_name: str, position: str) -> str:
    return f"SELECT rn, cnt FROM ( SELECT tg_id, ROW_NUMBER() OVER (" \
           f"ORDER BY {column_name} DESC NULLS LAST) AS rn, " \
           f"COUNT() OVER () AS cnt FROM users WHERE position = '{position}')"


async def ratings_query(column_name: str, position: str,
                        where_name: str, where_value: str) -> str:
    return f"SELECT rn, cnt FROM(SELECT tg_id, ROW_NUMBER() OVER" \
           f"(ORDER BY {column_name} DESC NULLS LAST) AS rn," \
           f" COUNT() OVER () AS cnt" \
           f" FROM users WHERE position = '{position}'" \
           f" AND {where_name} = '{where_value}')"
