INSERT_USER = "INSERT INTO users (username, ter_num, password, region, "\
              "position, grade, kas, citimanager) " \
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

INSERT_PRACTICE_MR = "INSERT INTO best_practice_mr (bp_id, username, "\
                     "kas, tg_id, datetime_added, desc, file_link) "\
                     "VALUES (?, ?, ?, ?, ?, ?, ?)"

INSERT_PRACTICE = "INSERT INTO best_practice (region, name, desc, " \
                  "user_added, datetime_added, datetime_start, datetime_stop,"\
                  " file_link) VALUES (?, ?, ?, ?, ?, ?, ?, ?) "

BP_KAS = "UPDATE best_practice_mr SET kas_approved = ? WHERE id = ?"

BP_CM = "UPDATE best_practice_mr SET cm_approved = ? WHERE id = ?"

DELETE_BP = "DELETE FROM best_practice WHERE name = ?"

DELETE_BP_MR = "DELETE FROM best_practice_mr WHERE id = ?"

CM_TG_ID = "SELECT tg_id FROM users WHERE username = (SELECT citimanager " \
           "FROM users WHERE tg_id = ?)"

VOTE_BP = "INSERT INTO best_practice_vote (tg_id, photo_id, is_voted) " \
          "VALUES (?, ?, ?)"

LIKES_UP = "UPDATE best_practice_mr SET likes = likes + 1 WHERE id = ?"

TOP10 = "SELECT * FROM best_practice_mr WHERE bp_id = ? AND posted = True " \
        "ORDER BY likes DESC LIMIT 10"


async def update_value(table: str, column_name: str, where_name: str) -> str:
    return f"UPDATE {table} SET {column_name} = ? WHERE {where_name} = ?"


async def get_value(value: str, table: str) -> str:
    return f"SELECT {value} FROM {table}"


async def ratings_query_all(column_name: str, sort_type: str,
                            position: str) -> str:
    return f"SELECT rn, cnt FROM (SELECT tg_id, DENSE_RANK() OVER (" \
           f"ORDER BY {column_name} {sort_type} NULLS LAST) AS rn, " \
           f"COUNT() OVER () AS cnt FROM users WHERE" \
           f" position = '{position}' AND {column_name} <> 0)"


async def ratings_query(column_name: str, sort_type: str, position: str,
                        where_name: str, where_value: str) -> str:
    return f"SELECT rn, cnt FROM (SELECT tg_id, DENSE_RANK() OVER (" \
           f"ORDER BY {column_name} {sort_type} NULLS LAST) AS rn, " \
           f"COUNT() OVER () AS cnt FROM users WHERE" \
           f" position = '{position}' AND {column_name} <> 0 AND" \
           f" {where_name} = '{where_value}' )"
