import asyncio
from datetime import date, timedelta
from typing import Optional

from isdayoff import AsyncProdCalendar


async def add_working_days(
        start_date: date,
        days_to_add: int,
        calendar: AsyncProdCalendar,
        callback: Optional[callable] = None) -> date:
    current_date = start_date
    added_days = 0

    while added_days < days_to_add:
        current_date += timedelta(days=1)
        day_type = await calendar.check(current_date)

        if day_type == 0:
            added_days += 1
            if callback:
                await callback(current_date, added_days, days_to_add)

    return current_date


# Пример использования
async def example_usage():
    async with AsyncProdCalendar() as calendar:
        start_date = date(2025, 4, 30)
        result_date = await add_working_days(start_date, 10, calendar)

        print(f"Начальная дата: {start_date}")
        print(f"Дата после добавления 10 рабочих дней: {result_date}")


async def main():
    await example_usage()

if __name__ == "__main__":
    asyncio.run(main())
