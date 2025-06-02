import logging
import aiosqlite as asq
from typing import List, Union, Any

from utils.create_tables import TABLES


class BotDB:
    def __init__(self, db_file: str):
        self.connection = None
        self._db_file = db_file

    async def __aenter__(self):
        await self.create_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_connection()

    async def create_table(self):
        async with asq.connect(self._db_file) as conn:
            await conn.executescript(TABLES)
            await conn.commit()
            logging.info('Tables created!')
            return None

    async def create_connection(self):
        if self.connection is None:
            self.connection = await asq.connect(self._db_file)
        return self.connection

    async def close_connection(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    def _prepare_values(self, query: str, args: tuple, kwargs: dict) ->\
            tuple[str, list[Any] | str]:
        if args:
            values = list(args)
        elif kwargs:
            query += ' WHERE ' + ' AND '.join(
                ['' + k + ' = ?' for k in kwargs])
            values = list(kwargs.values())
        else:
            values = ''
        return query, values

    async def get_one(self, query: str, *args, **kwargs):
        if self.connection is None:
            await self.create_connection()
        query, values = self._prepare_values(query, args, kwargs)
        async with self.connection.execute(query, values) as cursor:
            return await cursor.fetchone()

    async def get_all(self, query: str, *args, **kwargs):
        if self.connection is None:
            await self.create_connection()
        query, values = self._prepare_values(query, args, kwargs)
        async with self.connection.execute(query, values) as cursor:
            return await cursor.fetchall()

    async def post(self, query: str, *args, **kwargs):
        if self.connection is None:
            await self.create_connection()
        if args:
            values = list(args)
        elif kwargs:
            values = list(kwargs.values())
        else:
            values = ''
        try:
            await self.connection.execute(query, values)
            await self.connection.commit()
        except Exception as e:
            await self.connection.rollback()
            logging.error('INSERT FAILED: %s', str(e))
            raise

    async def postmany(self, query: str, values_list: List[Union[tuple, list]]):
        if self.connection is None:
            await self.create_connection()
        try:
            await self.connection.executemany(query, values_list)
            await self.connection.commit()
        except Exception as e:
            await self.connection.rollback()
            logging.error('BULK INSERT FAILED: %s', str(e))
            raise
