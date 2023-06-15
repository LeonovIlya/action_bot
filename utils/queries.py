# запросы к таблице planograms
shop_list = "SELECT DISTINCT chain_name FROM planograms"
magnit_list = "SELECT DISTINCT shop_name FROM planograms"
name_query = "SELECT DISTINCT name FROM planograms"
file_query = "SELECT file_link FROM planograms"

kpi_mr_query = "SELECT plan_pss, fact_pss, [%_pss], plan_osa, fact_osa, " \
               "[%_osa], plan_tt, fact_tt, [%_tt], plan_visits, fact_visits," \
               "[%_visits], isa_osa FROM users"


async def get_value_by_tg_id(value: str) -> str:
    return f"SELECT {value} FROM users"


async def ratings_query_all(column_name: str) -> str:
    return f"SELECT rank FROM ( SELECT *, ROW_NUMBER() OVER (" \
           f"ORDER BY {column_name} DESC NULLS LAST) AS rank FROM users)"


async def ratings_query(column_name: str,
                        where_name: str,
                        where_value: str) -> str:
    return f"SELECT rank FROM" \
           f"(SELECT *, ROW_NUMBER() OVER" \
           f"(ORDER BY {column_name} DESC NULLS LAST)" \
           f"AS rank FROM users WHERE {where_name} = '{where_value}')"