import logging
import aiosqlite as asq

from utils.create_tables import tables


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
            await conn.executescript(tables)
            await conn.commit()
            logging.info('tables created')
            return None

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def get_list(self, query: str, **kwargs):
        if self.connection is None:
            await self.create_connection()
        if kwargs:
            query += ' WHERE ' + ' AND '.join(
                ['' + k + ' = ?' for k in kwargs.keys()])
            values = list(kwargs.values())
        else:
            values = ''
        async with self.connection.execute(query, values) as cursor:
            result = await cursor.fetchall()
            return [i for i in result]

    async def get_one(self, query: str, **kwargs):
        if self.connection is None:
            await self.create_connection()
        if kwargs:
            query += ' WHERE ' + ' AND '.join(
                ['' + k + ' = ?' for k in kwargs.keys()])
            values = list(kwargs.values())
        else:
            values = ''
        async with self.connection.execute(query, values) as cursor:
            return await cursor.fetchone()

    async def get_all(self, query: str, **kwargs):
        if self.connection is None:
            await self.create_connection()
        if kwargs:
            query += ' WHERE ' + ' AND '.join(
                ['' + k + ' = ?' for k in kwargs.keys()])
            values = list(kwargs.values())
        else:
            values = ''
        async with self.connection.execute(query, values) as cursor:
            return await cursor.fetchall()

    async def post(self, query: str, **kwargs):
        if self.connection is None:
            await self.create_connection()
        values = list(kwargs.values())
        await self.connection.execute(query, values)
        await self.connection.commit()
        logging.info(f'NEW INSERT:\nQUERY: {query}\nVALUES: {values}')
