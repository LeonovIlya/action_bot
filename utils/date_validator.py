"""Модуль для проверки валидности даты в формате ДД.ММ.ГГГГ."""

import re
from datetime import date as dt

DATE_PATTERN = re.compile(
    r'^(0[1-9]|[12][0-9]|3[01])\.'  # день (01–31)
    r'(0[1-9]|1[0-2])\.'            # месяц (01–12)
    r'(19\d\d|20\d\d|2100)$')        # год (1900–2100)

async def is_valid_date(date_str: str, future: bool) -> bool:
    """Проверяет, является ли строка корректной датой в формате ДД.ММ.ГГГГ."""
    match = DATE_PATTERN.match(date_str)
    if not match:
        return False
    try:
        day, month, year = map(int, date_str.split('.'))
        input_date = dt(year=year, month=month, day=day)
        if future and input_date < dt.today():
            return False
        return True
    except ValueError:
        return False
