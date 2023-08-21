import logging
import aiosqlite as asq

from utils.create_tables import TABLES


class BotDB:
    def __init__(self, db_file: str):
        self.connection = None
        self._db_file = db_file

    async def create_connection(self):
        if self.connection is None:
            self.connection = await asq.connect(self._db_file)
        return self.connection

    async def create_table(self):
        async with asq.connect(self._db_file) as conn:
            await conn.executescript(TABLES)
            await conn.commit()
            logging.info('Tables created!')
            return None

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def get_one(self, query: str, *args, **kwargs):
        if self.connection is None:
            await self.create_connection()
        if args:
            values = list(args)
        elif kwargs:
            query += ' WHERE ' + ' AND '.join(
                ['' + k + ' = ?' for k in kwargs])
            values = list(kwargs.values())
        else:
            values = ''
        async with self.connection.execute(query, values) as cursor:
            return await cursor.fetchone()

    async def get_all(self, query: str, *args, **kwargs):
        if self.connection is None:
            await self.create_connection()
        if args:
            values = list(args)
        elif kwargs:
            query += ' WHERE ' + ' AND '.join(
                ['' + k + ' = ?' for k in kwargs])
            values = list(kwargs.values())
        else:
            values = ''
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
        await self.connection.execute(query, values)
        await self.connection.commit()
        logging.info('NEW INSERT:\nQUERY: %s \nVALUES: %s', query, values)
