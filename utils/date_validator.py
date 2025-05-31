import re
from datetime import datetime as dt


date_pattern = re.compile(
    r'^(0[1-9]|[12][0-9]|3[01])\.'  # день (01-31)
    r'(0[1-9]|1[0-2])\.'  # месяц (01-12)
    r'(19\d\d|20\d\d|2100)$')  # год (1900-2100)


async def is_valid_date(date_str: str) -> bool:
    if not date_pattern.match(date_str):
        return False
    try:
        day, month, year = map(int, date_str.split('.'))
        input_date = dt(year=year, month=month, day=day).date()
        today = dt.now().date()
        if input_date < today:
            return False
        return True
    except ValueError:
        return False
