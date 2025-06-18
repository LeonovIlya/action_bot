"""Модуль для работы с датами: парсинг и добавление рабочих дней."""

import logging
from datetime import date, datetime, timedelta
from typing import Optional, Union, List, Callable, Awaitable
from adaptation.isdayoff import AsyncProdCalendar, DayType


logger = logging.getLogger("bot")


async def parse_date(date_str: str) -> Optional[date]:
    """Преобразует строку формата DD.MM.YYYY в объект date."""
    try:
        parsed_date = datetime.strptime(
            date_str.strip(), "%d.%m.%Y").date()
        logger.debug(f"Дата успешно распарсена: {parsed_date}")
        return parsed_date
    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка парсинга даты '{date_str}': {e}",
                     exc_info=True)
        raise ValueError(f"Ошибка парсинга даты: {str(e)}") from e


async def add_working_days(
        start_date: date,
        days_to_add: Union[int, List[int]],
        calendar: AsyncProdCalendar = AsyncProdCalendar(
            locale="ru", cache=True, freshness=timedelta(days=30)),
        callback: Optional[Callable[[date, int, int], Awaitable[None]]] = None)\
        -> Union[str, List[str]]:
    """Добавляет указанное количество рабочих дней к дате, пропуская выходные
    и праздники. """

    async def calculate_single_date(base_date: date, quantity: int) -> date:
        current_date = base_date
        added_days = 0
        while added_days < quantity:
            current_date += timedelta(days=1)
            day_type = await calendar.check(current_date)
            if day_type == DayType.WORKING:
                added_days += 1
                if callback:
                    await callback(current_date, added_days, quantity)
        return current_date

    logger.info(f"Добавление рабочих дней к дате {start_date}: {days_to_add}")
    if isinstance(days_to_add, int):
        result_date = await calculate_single_date(start_date, days_to_add)
        formatted_result = datetime.strftime(result_date, '%d.%m.%Y')
        logger.debug(f"Результат: {formatted_result}")
        return formatted_result
    elif isinstance(days_to_add, list):
        formatted_results = []
        for days in days_to_add:
            result_date = await calculate_single_date(start_date, days)
            formatted_result = datetime.strftime(result_date, '%d.%m.%Y')
            formatted_results.append(formatted_result)
            logger.debug(f"Добавлено {days} дней → {formatted_result}")
        return formatted_results
    else:
        logger.error("days_to_add должен быть int или list[int]")
        raise TypeError("days_to_add должен быть int или list[int]")
