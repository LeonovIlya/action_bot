# запросы к таблице planograms
shop_list = "SELECT DISTINCT chain_name FROM planograms"
magnit_list = "SELECT DISTINCT shop_name FROM planograms"
name_query = "SELECT DISTINCT name FROM planograms"
file_query = "SELECT file_link FROM planograms"

BP_NAME = "SELECT name, desc, datetime_start, datetime_stop, pics FROM "\
          "best_practice"
MAX_ID = "SELECT MAX(id) FROM best_practice"

INSERT_PRACTICE = "INSERT INTO best_practice (name, desc, user_added, "\
                  "datetime_added, datetime_start, datetime_stop, is_active, "\
                  "pics) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "

UPDATE_TG_ID = "UPDATE users SET tg_id = ? WHERE ter_num = ?"

kpi_mr_query = "SELECT plan_pss, fact_pss, [%_pss], plan_osa, fact_osa, "\
               "[%_osa], plan_tt, fact_tt, [%_tt], plan_visits, fact_visits,"\
               "[%_visits], isa_osa FROM users"


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
