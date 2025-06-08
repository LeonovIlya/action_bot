from datetime import date, datetime, timedelta
from typing import Optional, Union, List

from adaptation.isdayoff import AsyncProdCalendar


async def parse_date(date_str: str) -> Optional[date]:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except Exception as e:
        raise ValueError(f"Ошибка парсинга даты: {str(e)}")


async def add_working_days(
        start_date: date,
        days_to_add: Union[int, List[int]],
        calendar: AsyncProdCalendar = AsyncProdCalendar(),
        callback: Optional[callable] = None) -> Union[str, List[str]]:

    async def calculate_single_date(base_date: date, days: int) -> date:
        current_date = base_date
        added_days = 0
        while added_days < days:
            current_date += timedelta(days=1)
            day_type = await calendar.check(current_date)
            if day_type == 0:  # Рабочий день
                added_days += 1
                if callback:
                    await callback(current_date, added_days, days)
        return current_date
    if isinstance(days_to_add, int):
        result_date = await calculate_single_date(start_date, days_to_add)
        return datetime.strftime(result_date, '%d.%m.%Y')
    elif isinstance(days_to_add, list):
        result_dates = []
        for days in days_to_add:
            result_date = await calculate_single_date(start_date, days)
            result_dates.append(datetime.strftime(result_date, '%d.%m.%Y'))
        return result_dates
    else:
        raise TypeError("days_to_add должен быть int или list[int]")
