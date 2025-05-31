from datetime import date, datetime, timedelta
from typing import Optional

from adaptation.isdayoff import AsyncProdCalendar


async def parse_date(date_str: str) -> Optional[date]:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except Exception as e:
        raise ValueError(f"Ошибка парсинга даты: {str(e)}")


async def add_working_days(
        start_date: date,
        days_to_add: int,
        calendar: AsyncProdCalendar = AsyncProdCalendar(),
        callback: Optional[callable] = None) -> str:
    current_date = start_date
    added_days = 0

    while added_days < days_to_add:
        current_date += timedelta(days=1)
        day_type = await calendar.check(current_date)

        if day_type == 0:
            added_days += 1
            if callback:
                await callback(current_date, added_days, days_to_add)

    return datetime.strftime(current_date, '%d.%m.%Y')
