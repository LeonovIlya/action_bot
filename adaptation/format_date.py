import asyncio
from datetime import datetime
from typing import Optional
from workdays import add_working_days
from isdayoff import AsyncProdCalendar


async def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except (ValueError, TypeError):
        return None


async def main():
    date_tuple = await parse_date("30.04.2025")
    async with AsyncProdCalendar() as calendar:
        r = await add_working_days(date_tuple, 10, calendar)
        print(r)

if __name__ == "__main__":
    asyncio.run(main())
