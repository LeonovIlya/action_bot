"""Модуль для работы с кэшированием колонок таблиц и получения записей за
сегодня. """

import logging
import json
import hashlib
from typing import List, Dict, Optional, Any
from redis.asyncio import Redis, RedisError
from redis.exceptions import ConnectionError as RedisConnectionError
from loader import db
import config

logger = logging.getLogger("bot")


class AsyncRedisColumnCache:
    """Класс для работы с кэшированием колонок таблиц и получения записей за
    сегодня. """

    def __init__(self, redis: Optional[Redis] = None):
        """Инициализация кэша для хранения информации о колонках."""
        self.redis = redis or Redis(
            host=config.REDIS_HOST,
            password=config.REDIS_PASSWORD,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=2)
        self._table_columns_cache: Dict[str, List[str]] = {}

    def _get_cache_key(self, table_name: str) -> str:
        """Генерирует безопасный ключ для кэша."""
        if not isinstance(table_name, str):
            raise ValueError("Название таблицы должно быть строкой")
        return f"async_column_cache:" \
               f"{hashlib.sha256(table_name.encode()).hexdigest()} "

    async def get_columns(self, table_name: str) -> List[str]:
        """Получает список колонок с префиксом 'date_' из кэша или БД."""
        if table_name in self._table_columns_cache:
            logger.debug(f"Колонки для {table_name} найдены в локальном кэше")
            return self._table_columns_cache[table_name]
        cache_key = self._get_cache_key(table_name)
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                columns = json.loads(cached)
                logger.debug(f"Колонки для {table_name} загружены из Redis")
                self._table_columns_cache[table_name] = columns
                return columns
        except RedisConnectionError:
            logger.warning("Redis недоступен, пропускаем кэширование")
        except RedisError as e:
            logger.warning(f"Ошибка чтения из Redis: {e}")
        columns = await self._fetch_from_db(table_name)
        if not isinstance(columns, list):
            raise TypeError("Ожидается список названий колонок")
        self._table_columns_cache[table_name] = columns
        if not isinstance(self.redis.connection_pool.connection_kwargs.get('password'),
                          type(None)):
            try:
                await self.redis.setex(cache_key, 2592000, json.dumps(columns))
                logger.debug(f"Колонки для {table_name} сохранены в Redis")
            except RedisError as e:
                logger.warning(f"Ошибка записи в Redis: {e}")
        return columns

    async def _fetch_from_db(self, table_name: str) -> List[str]:
        """Получает список колонок из базы данных."""
        try:
            rows = await db.get_all(f"PRAGMA table_info({table_name})")
            logger.debug(f"Получено {len(rows)} колонок из таблицы "
                         f"{table_name}")
            return [row[1] for row in rows if row[1].startswith('date_')]
        except Exception as e:
            logger.error(f"Не удалось получить колонки для {table_name}: {e}",
                         exc_info=True)
            return []

    async def invalidate_cache(self, table_name: str) -> None:
        """Сбрасывает кэш для указанной таблицы."""
        cache_key = self._get_cache_key(table_name)
        try:
            await self.redis.delete(cache_key)
            logger.info(f"Кэш для таблицы {table_name} очищен")
        except RedisError as e:
            logger.warning(f"Ошибка при удалении кэша: {e}")

    async def close(self) -> None:
        """Закрывает соединение с Redis."""
        try:
            await self.redis.close()
            logger.info("Соединение с Redis закрыто")
        except RedisError as e:
            logger.error(f"Ошибка при закрытии Redis: {e}")


async def get_todays_records(
        table_name: str,
        today: str,
        cache: Optional[AsyncRedisColumnCache] = None) -> List[Dict[str, Any]]:
    """Возвращает записи из таблицы, где одна из датированных колонок
    совпадает с today. """
    logger.info(f"Получение записей за сегодня из таблицы '{table_name}'")
    own_cache = False
    if cache is None:
        cache = AsyncRedisColumnCache()
        own_cache = True
    try:
        date_columns = await cache.get_columns(table_name)
        if not date_columns:
            logger.warning(f"В таблице '{table_name}' нет колонок с префиксом "
                           f"'date_'")
            return []
        conditions = " OR ".join([f"`{col}` = ?" for col in date_columns])
        params = [today] * len(date_columns) + [False]
        query = (
            f"SELECT * FROM {table_name} "
            f"WHERE ({conditions}) AND is_archive = ?")
        rows = await db.get_all(query, *params)
        if not rows:
            logger.debug(f"Нет записей за сегодня в таблице '{table_name}'")
            return []
        cursor = await db.get_all(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor]
        result = []
        for row in rows:
            record = dict(zip(columns, row))
            matched_columns = [col for col in date_columns if str(
                record.get(col)) == str(today)]
            if matched_columns:
                record['matched_columns'] = matched_columns
                result.append(record)
        logger.info(f"Найдено {len(result)} записей в таблице '{table_name}' "
                    f"на сегодня")
        return result

    except Exception as e:
        logger.error(f"Ошибка при получении записей за сегодня: {e}",
                     exc_info=True)
        return []
    finally:
        if own_cache:
            await cache.close()
