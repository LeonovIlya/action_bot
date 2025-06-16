"""Модуль для работы с базой данных SQLite (асинхронный)."""

import logging
import aiosqlite
from typing import List, Union, Any, Optional

from utils.create_tables import TABLES

logger = logging.getLogger(__name__)


class BotDB:
    """Класс для работы с базой данных SQLite."""
    def __init__(self, db_file: str):
        """Инициализация класса."""
        self.connection: Optional[aiosqlite.Connection] = None
        self._db_file = db_file

    async def create_table(self):
        """Создаёт таблицы, если они ещё не созданы."""
        async with aiosqlite.connect(self._db_file) as conn:
            await conn.executescript(TABLES)
            await conn.commit()
            logger.info('Таблицы успешно созданы!')

    async def create_connection(self):
        """Создаёт новое соединение с БД."""
        if self.connection is None:
            self.connection = await aiosqlite.connect(self._db_file)
            logger.debug('Новое соединение с БД установлено')
        return self.connection

    async def close_connection(self):
        """Закрывает соединение с БД."""
        if self.connection is not None:
            await self.connection.close()
            self.connection = None
            logger.debug('Соединение с БД закрыто')

    def _prepare_values(self, query: str, args: tuple, kwargs: dict) -> tuple:
        """Подготавливает SQL-запрос и значения."""
        values = list(args) if args else []
        if kwargs:
            query += ' WHERE ' + ' AND '.join([f"{k} = ?" for k in kwargs])
            values += list(kwargs.values())
        return query, values

    async def get_one(self, query: str, *args, **kwargs):
        """Выполняет SELECT и возвращает одну строку."""
        if self.connection is None:
            await self.create_connection()
        query, values = self._prepare_values(query, args, kwargs)
        async with self.connection.execute(query, values) as cursor:
            return await cursor.fetchone()

    async def get_all(self, query: str, *args, **kwargs):
        """Выполняет SELECT и возвращает все строки."""
        if self.connection is None:
            await self.create_connection()
        query, values = self._prepare_values(query, args, kwargs)
        async with self.connection.execute(query, values) as cursor:
            return await cursor.fetchall()

    async def post(self, query: str, *args, **kwargs):
        """Выполняет INSERT/UPDATE/DELETE запрос."""
        if self.connection is None:
            await self.create_connection()
        _, values = self._prepare_values(query, args, kwargs)
        try:
            await self.connection.execute(query, values)
            await self.connection.commit()
        except Exception as e:
            await self.connection.rollback()
            logger.error('INSERT FAILED: %s', str(e))
            raise

    async def postmany(self, query: str, values_list: List[Union[tuple, list]]):
        """Выполняет массовый INSERT."""
        if self.connection is None:
            await self.create_connection()
        try:
            await self.connection.executemany(query, values_list)
            await self.connection.commit()
        except Exception as e:
            await self.connection.rollback()
            logger.error('BULK INSERT FAILED: %s', str(e))
            raise
