"""Модуль для определения рабочих/выходных дней через API isdayoff.ru."""

from enum import IntEnum
from datetime import date, timedelta, datetime
from pathlib import Path
from typing import Optional, Dict, List
import aiofiles
import aiohttp
import logging

logger = logging.getLogger("bot")


class ServiceNotRespond(Exception):
    """Исключение: сервис не отвечает или вернул неверный формат."""
    pass


class DayType(IntEnum):
    """Представление типа дня — рабочий или выходной."""
    WORKING = 0
    NOT_WORKING = 1


class AsyncProdCalendar:
    """Асинхронный клиент для получения информации о рабочих днях через
    isdayoff.ru."""
    URL = "https://isdayoff.ru/"
    DATE_FORMAT = "%Y%m%d"
    CACHE_FILE_FORMAT = "isdayoff_{year}_{locale}.txt"
    LOCALES = ("ru", "ua", "kz", "by", "us")

    def __init__(
            self,
            locale: str = "ru",
            cache: bool = True,
            cache_dir: str = "cache/",
            freshness: timedelta = timedelta(days=30)):
        """Инициализация календаря."""
        if locale not in self.LOCALES:
            raise ValueError(f"Locale должен быть одним из {self.LOCALES}")
        self.locale = locale
        self.cache = cache
        self.cache_dir = Path(cache_dir)
        self.freshness = freshness
        self._memory_cache: Dict[int, List[int]] = {}
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def check(self, day: date) -> DayType:
        """Проверяет тип дня (рабочий/выходной)."""
        logger.debug(f"Проверка дня: {day} ({self.locale})")
        year = day.year
        day_of_year = day.timetuple().tm_yday - 1
        if self.cache:
            if year in self._memory_cache:
                return DayType(self._memory_cache[year][day_of_year])
            cache_file = self._get_cache_file_path(year)
            try:
                if await self._load_cache_file(cache_file):
                    return DayType(self._memory_cache[year][day_of_year])
            except (FileNotFoundError, ValueError):
                logger.info(f"Кэш за {year} год не найден или устарел")
        return await self._download_and_check(year, day_of_year)

    async def _download_and_check(self, year: int, day_idx: int) -> DayType:
        """Загружает данные за год и возвращает тип дня."""
        logger.info(f"Загрузка данных за {year} год")
        try:
            data = await self._fetch_year_data(year)
            self._memory_cache[year] = [int(c) for c in data]
            await self._save_to_cache(year, data)
            return DayType(self._memory_cache[year][day_idx])
        except Exception as e:
            logger.error(f"Не удалось загрузить данные за {year}: {e}",
                         exc_info=True)
            raise ServiceNotRespond(f"Ошибка при загрузке данных за {year} год")

    async def _fetch_year_data(self, year: int) -> str:
        """Получает строку данных за год с API."""
        if not self._session:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                        f"{self.URL}api/getdata", params={"year": year,
                                                          "cc": self.locale}) \
                        as resp:
                    if resp.status != 200:
                        raise ServiceNotRespond(
                            f"API не отвечает: {resp.status}")
                    return await resp.text()
        else:
            async with self._session.get(
                    f"{self.URL}api/getdata", params={"year": year,
                                                      "cc": self.locale}) \
                    as resp:
                if resp.status != 200:
                    raise ServiceNotRespond(f"API не отвечает: {resp.status}")
                return await resp.text()

    async def _save_to_cache(self, year: int, content: str):
        """Сохраняет данные в файл кэша."""
        cache_file = self._get_cache_file_path(year)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        try:
            async with aiofiles.open(cache_file, "w") as f:
                await f.write(datetime.now().isoformat() + "\n")
                await f.write(content)
            logger.debug(f"Кэш за {year} сохранён")
        except Exception as e:
            logger.warning(f"Не удалось сохранить кэш за {year}: {e}")

    def _get_cache_file_path(self, year: int) -> Path:
        filename = self.CACHE_FILE_FORMAT.format(year=year, locale=self.locale)
        return self.cache_dir / filename

    async def _load_cache_file(self, cache_file: Path) -> bool:
        """Загружает кэш из файла."""
        if not cache_file.exists():
            raise FileNotFoundError(f"Файл кэша не найден: {cache_file}")
        async with aiofiles.open(cache_file, "r") as f:
            first_line = await f.readline()
            try:
                cache_date = datetime.fromisoformat(first_line.strip())
                if cache_date + self.freshness < datetime.now():
                    raise ValueError("Кэш устарел")
            except ValueError as e:
                logger.warning(f"Ошибка чтения кэша: {e}")
                raise
            content = await f.read()
            year = int(cache_file.stem.split("_")[1])
            self._memory_cache[year] = [int(c) for c in content]
            logger.debug(f"Кэш за {year} загружен")
            return True

    async def today(self) -> DayType:
        """Возвращает тип сегодняшнего дня."""
        return await self.check(date.today())
