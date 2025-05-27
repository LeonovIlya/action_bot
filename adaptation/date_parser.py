import asyncio
import logging
import json
import hashlib
from pprint import pp
from typing import List, Dict, Union

import config
from redis.asyncio import Redis, RedisError
from loader import db
from utils.jobs import get_now


class AsyncRedisColumnCache:
    def __init__(self):
        self.redis = Redis(
            password=config.REDIS_PASSWORD,
            host=config.REDIS_HOST,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=2)
        self._table_columns_cache = {}

    def _get_cache_key(self, table_name: str) -> str:
        """Генерирует безопасный ключ для кэша"""
        if not isinstance(table_name, str):
            raise ValueError("Table name must be a string")
        return f"async_column_cache:{hashlib.sha256(table_name.encode()).hexdigest()}"

    async def get_columns(self, table_name: str) -> list[dict]:
        """Получает колонки с префиксом date_ с кэшированием"""
        if not isinstance(table_name, str):
            raise ValueError("Table name must be a string")

        if table_name in self._table_columns_cache:
            return self._table_columns_cache[table_name]
        cache_key = self._get_cache_key(table_name)
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                columns = json.loads(cached)
                self._table_columns_cache[table_name] = columns
                return columns
        except RedisError as e:
            logging.warning(f"Redis cache read failed: {e}")
        columns = await self._fetch_from_db(table_name)
        if not isinstance(columns, list):
            raise TypeError("Expected list of columns")
        self._table_columns_cache[table_name] = columns
        try:
            await self.redis.setex(
                cache_key,
                2592000,
                json.dumps(columns))
        except RedisError as e:
            logging.warning(f"Redis cache write failed: {e}")

        return columns

    async def _fetch_from_db(self, table_name: str) -> Union[list[dict], None]:
        """Безопасно получает список колонок из БД"""
        try:
            rows = await db.get_all(f"PRAGMA table_info({table_name})")
            return [row[1] for row in rows if row[1].startswith('date_')]
        except Exception as e:
            logging.error(f"Failed to fetch columns for {table_name}: {e}")
            return []


    async def invalidate_cache(self, table_name: str):
        """Сбрасываем кэш при изменении схемы"""
        cache_key = self._get_cache_key(table_name)
        await self.redis.delete(cache_key)

    async def close(self):
        """Корректно закрывает соединения"""
        try:
            await self.redis.close()
        except RedisError as e:
            logging.error(f"Error closing Redis connection: {e}")



async def get_todays_records(table_name: str, cache: AsyncRedisColumnCache =
AsyncRedisColumnCache()) -> Union[List[Dict], None]:

    """Основная функция для получения записей с сегодняшней датой"""
    try:
        date_columns = await cache.get_columns(table_name)
        if not date_columns:
            logging.error(f"No date columns in table {table_name}")
            return []
        today = await get_now()
        conditions = " OR ".join([f"`{col}` = ?" for col in date_columns])
        params = [today] * len(date_columns)
        query = f"SELECT * FROM {table_name} WHERE {conditions}"
        rows = await db.get_all(query, *params)
        if not rows:
            return None
        result = []
        cursor = await db.get_all(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor]
        for row in rows:
            record = dict(zip(columns, row))
            matched_columns = [
                col for col in date_columns
                if str(record.get(col)) == str(today)]
            if matched_columns:
                record['matched_columns'] = ", ".join(str(col) for col in matched_columns)
                result.append(record)
        await cache.close()
        return result

    except Exception as e:
        logging.error("Error fetching today's records: %s", str(e))
        return []


async def main():
    records = await get_todays_records(
        table_name="adaptation")
    pp(records)

if __name__ == "__main__":
    asyncio.run(main())