from enum import IntEnum
from datetime import date, timedelta, datetime
from pathlib import Path
import aiofiles
import aiohttp
import asyncio


class ServiceNotRespond(Exception):
    pass


class DayType(IntEnum):
    WORKING = 0
    NOT_WORKING = 1


class AsyncProdCalendar:
    URL = 'https://isdayoff.ru/'
    DATE_FORMAT = '%Y%m%d'
    CACHE_FILE_FORMAT = '%sisdayoff%i%s.txt'
    LOCALES = ('ru', 'ua', 'kz', 'by', 'us')

    def __init__(self, locale: str = 'ru', cache: bool = True, cache_dir: str = 'cache/',
                 cache_year: int = date.today().year, freshness: timedelta = timedelta(days=30)):
        if locale not in self.LOCALES:
            raise ValueError('locale must be in ' + str(self.LOCALES))
        self.locale = locale
        self.cache = cache
        self.cache_dir = cache_dir
        self.freshness = freshness
        self._cache_year = cache_year
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        if self.cache:
            await self.cache_year(self._cache_year, forced=False)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check(self, day: date) -> DayType:
        if self.cache:
            return await self._get_cache(day)
        else:
            async with self.session.get(
                    self.URL + day.strftime(self.DATE_FORMAT),
                    params={'cc': self.locale}
            ) as resp:
                if resp.status != 200:
                    raise ServiceNotRespond
                return DayType(int(await resp.text()))

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

    async def cache_year(self, year: int, forced: bool = True) -> Path:
        Path(self.cache_dir).mkdir(exist_ok=True, parents=True)
        cache_file = Path(self.CACHE_FILE_FORMAT % (self.cache_dir, year, self.locale))

        if forced or not cache_file.is_file():
            await self._write_cache(year, cache_file)
        elif not await self._is_cache_fresh(cache_file):
            await self._write_cache(year, cache_file)

        return cache_file.absolute()

    async def _write_cache(self, year: int, cache_file: Path):
        async with self.session.get(
                self.URL + 'api/getdata',
                params={'year': year, 'cc': self.locale}
        ) as resp:
            if resp.status != 200:
                raise ServiceNotRespond()

            async with aiofiles.open(cache_file.absolute(), 'w') as f:
                await f.write(datetime.now().isoformat() + '\n')
                await f.write(await resp.text())

    async def _is_cache_fresh(self, cache_file: Path) -> bool:
        async with aiofiles.open(cache_file.absolute()) as f:
            cache_date = datetime.fromisoformat((await f.readline()).strip())
            return cache_date + self.freshness >= datetime.now()

    async def _get_cache(self, day: date) -> DayType:
        async with aiofiles.open(await self.cache_year(day.year, forced=False)) as f:
            await f.readline()
            content = await f.read()
            return DayType(int(content[day.timetuple().tm_yday - 1]))


async def example_usage():
    async with AsyncProdCalendar() as prodcal:
        for i in range(1, 30):
            check_date = date(2025, 6, i)
            result = await prodcal.check(check_date)
            print(f"{check_date} - {'Выходной' if result else 'рабочий день'}")


if __name__ == "__main__":
    asyncio.run(example_usage())
