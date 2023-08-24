NAME_QUERY = "SELECT DISTINCT name FROM planograms"

INSERT_USER = "INSERT INTO users (username, ter_num, password, region, "\
              "position, grade, kas, citimanager) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

INSERT_PRACTICE_MR = "INSERT INTO best_practice_mr (best_practice, user_id, "\
                     "kas, tg_id, datetime_added, desc, file_link) "\
                     "VALUES (?, ?, ?, ?, ?, ?, ?)"

INSERT_PRACTICE = "INSERT INTO best_practice (region, name, desc, " \
                  "user_added, datetime_added, datetime_start, datetime_stop,"\
                  " is_active, is_over, file_link) " \
                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "

BP_KAS = "UPDATE best_practice_mr SET kas_checked = ?, kas_approved = ? " \
         "WHERE id = ?"

BP_CM = "UPDATE best_practice_mr SET cm_checked = ?, cm_approved = ?, " \
        "is_active = ? WHERE id = ?"

DELETE_BP = "DELETE FROM best_practice WHERE name = ?"

DELETE_BP_MR = "DELETE FROM best_practice_mr WHERE id = ?"

CM_TG_ID = "SELECT tg_id FROM users WHERE username = (SELECT citimanager " \
           "FROM users WHERE tg_id = ?)"

GET_BP_PHOTOS = "SELECT * FROM best_practice_mr WHERE NOT EXISTS " \
                "(SELECT id FROM best_practice_vote WHERE " \
                "photo_id = best_practice_mr.id AND user_id = ?)"

VOTE_BP = "INSERT INTO best_practice_vote (user_id, photo_id, is_voted) " \
          "VALUES (?, ?, ?)"


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
