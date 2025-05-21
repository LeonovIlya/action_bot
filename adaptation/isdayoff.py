from enum import IntEnum
from datetime import date, timedelta, datetime
from pathlib import Path
import aiofiles
import aiohttp
import asyncio
from typing import Optional, Dict, List


class ServiceNotRespond(Exception):
    pass


class DayType(IntEnum):
    WORKING = 0
    NOT_WORKING = 1


class AsyncProdCalendar:
    URL = 'https://isdayoff.ru/'
    DATE_FORMAT = '%Y%m%d'
    CACHE_FILE_FORMAT = 'isdayoff_{year}_{locale}.txt'
    LOCALES = ('ru', 'ua', 'kz', 'by', 'us')

    def __init__(self, locale: str = 'ru', cache: bool = True,
                 cache_dir: str = 'cache/',
                 freshness: timedelta = timedelta(days=30)):
        if locale not in self.LOCALES:
            raise ValueError(f'Locale must be one of {self.LOCALES}')

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
        if not self.cache:
            return await self._fetch_with_temp_session(day)
        year = day.year
        day_of_year = day.timetuple().tm_yday - 1
        if year in self._memory_cache:
            return DayType(self._memory_cache[year][day_of_year])
        cache_file = self._get_cache_file_path(year)
        try:
            if await self._load_cache_file(cache_file):
                return DayType(self._memory_cache[year][day_of_year])
        except (FileNotFoundError, ValueError):
            pass

        return await self._download_with_temp_session(year, day_of_year)

    async def _fetch_with_temp_session(self, day: date) -> DayType:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.URL + day.strftime(self.DATE_FORMAT),
                    params={'cc': self.locale}
            ) as resp:
                if resp.status != 200:
                    raise ServiceNotRespond("API не отвечает")
                return DayType(int(await resp.text()))

    async def _download_with_temp_session(self, year: int,
                                          day_idx: int) -> DayType:
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        cache_file = self._get_cache_file_path(year)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.URL + 'api/getdata',
                    params={'year': year, 'cc': self.locale}
            ) as resp:
                if resp.status != 200:
                    raise ServiceNotRespond(
                        f"Ошибка при загрузке данных за {year} год")
                content = await resp.text()
                self._memory_cache[year] = [int(c) for c in content]
                async with aiofiles.open(cache_file, 'w') as f:
                    await f.write(datetime.now().isoformat() + '\n')
                    await f.write(content)
        return DayType(self._memory_cache[year][day_idx])

    def _get_cache_file_path(self, year: int) -> Path:
        filename = self.CACHE_FILE_FORMAT.format(year=year, locale=self.locale)
        return self.cache_dir / filename

    async def _load_cache_file(self, cache_file: Path) -> bool:
        if not cache_file.exists():
            raise FileNotFoundError(f"Файл кэша не найден: {cache_file}")
        async with aiofiles.open(cache_file, 'r') as f:
            first_line = await f.readline()
            cache_date = datetime.fromisoformat(first_line.strip())
            if cache_date + self.freshness < datetime.now():
                raise ValueError("Кэш устарел")
            content = await f.read()
            year = int(cache_file.stem.split('_')[1])
            self._memory_cache[year] = [int(c) for c in content]
            return True

    async def today(self) -> DayType:
        return await self.check(date.today())

    async def next(self, day: date, dtype: DayType) -> date:
        while await self.check(day) != dtype:
            day += timedelta(days=1)
        return day

    async def previous(self, day: date, dtype: DayType) -> date:
        while await self.check(day) != dtype:
            day -= timedelta(days=1)
        return day