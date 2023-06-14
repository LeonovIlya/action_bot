import logging
import aiosqlite as asq

from utils.create_tables import tables


class BotDB:
    def __init__(self, db_file):
        self.connection = None
        self._db_file = db_file

    async def create_table(self):
        async with asq.connect(self._db_file) as conn:
            await conn.executescript(tables)
            await conn.commit()
            logging.info(f'tables created')
            return None

    async def create_connection(self):
        if self.connection is None:
            self.connection = await asq.connect(self._db_file)
            self.connection.row_factory = asq.Row
        return self.connection

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    async def some_function(self, user_id):
        if self.connection is None:
            await self.create_connection()
        async with self.connection.execute(f'SELECT * FROM users WHERE id'
                                           f'={user_id}') as cursor:
            result = await cursor.fetchall()
            return result

    async def get_stuff_list(self, query, **kwargs):
        if self.connection is None:
            await self.create_connection()
        if kwargs:
            query += ' WHERE ' + ' AND '.join(['' + k + ' = ?' for k in kwargs.keys()])
            values = list(kwargs.values())
        else:
            values = ''
        async with self.connection.execute(query, values) as cursor:
            fetch = await cursor.fetchall()
            if int(len(fetch[0])) == 1:
                result = [i[0] for i in fetch]
            elif int(len(fetch[0])) == 2:
                result = [(i[0], str(i[1])) for i in fetch]
            return result

    async def get_stuff(self, query, **kwargs):
        if self.connection is None:
            await self.create_connection()
        query += ' WHERE ' + ' AND '.join(['' + k + ' = ?' for k in kwargs.keys()])
        values = list(kwargs.values())
        async with self.connection.execute(query, values) as cursor:
            fetch = await cursor.fetchone()
            return fetch[0]
