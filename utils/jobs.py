import logging
from datetime import datetime as dt
import redis
import aiofiles
from aiopath import AsyncPath

from aiogram import Dispatcher
from aiopath import AsyncPath

import config
from loader import db
from utils import queries


async def check_bp_start(dp: Dispatcher):
    try:
        now = dt.now().date()
        now = dt.strptime(str(now), '%Y-%m-%d')
        bp = await db.get_all(
            await queries.get_value(
                value='id',
                table='best_practice'
            ),
            datetime_start=now,
            is_active=False,
            over=False
        )
        if bp:
            for i in bp:
                data = await db.get_one(queries.BP_NAME,
                                        id=i[0]
                                        )
                datetime_start = dt.strptime(data[2], '%Y-%m-%d %H:%M:%S')
                datetime_stop = dt.strptime(data[3], '%Y-%m-%d %H:%M:%S')
                start = datetime_start.strftime('%d %B %Y')
                stop = datetime_stop.strftime('%d %B %Y')
                file = AsyncPath(str(data[4]))
                if await file.is_file():
                    async with aiofiles.open(str(data[4]), 'rb') as photo:
                        await dp.bot.send_photo(
                            chat_id=config.CHANNEL_ID,
                            photo=photo,
                            caption='С сегодняшнего дня доступна '
                                    'новая практика!\n\n'
                                    f'<b>{str(data[0])}</b>\n\n'
                                    f'{str(data[1])}\n\n'
                                    f'<b>Дата начала:</b>\n'
                                    f'{str(start)}\n\n'
                                    f'<b>Дата окончания:</b>\n'
                                    f'{str(stop)}')
                else:
                    await dp.bot.send_message(
                        chat_id=config.CHANNEL_ID,
                        text='С сегодняшнего дня доступна новая '
                             'практика!\n\n'
                             f'<b>{str(data[0])}</b>\n\n'
                             f'{str(data[1])}\n\n'
                             f'<b>Дата начала:</b>\n'
                             f'{str(start)}\n\n'
                             f'<b>Дата окончания:</b>\n'
                             f'{str(stop)}')
                await db.post(
                    await queries.update_value(
                        table='best_practice',
                        column_name='is_active',
                        where_name='id'
                    ),
                    value=True,
                    id=i[0]
                )
    except Exception as error:
        logging.info(f'Schedule error: {error}')


async def check_bp_stop(dp: Dispatcher):
    try:
        now = dt.now().date()
        now = dt.strptime(str(now), '%Y-%m-%d')
        bp = await db.get_all(
            await queries.get_value(
                value='id',
                table='best_practice'
            ),
            datetime_stop=now,
            is_active=True,
            over=False
        )
        if bp:
            for i in bp:
                data = await db.get_one(queries.BP_NAME,
                                        id=i[0])
                file = AsyncPath(str(data[4]))
                if await file.is_file():
                    async with aiofiles.open(str(data[4]), 'rb') as photo:
                        await dp.bot.send_photo(
                            chat_id=config.CHANNEL_ID,
                            photo=photo,
                            caption=f'Лучшая практика <b>{str(data[0])}</b> '
                                    f'закончилась')
                else:
                    await dp.bot.send_message(
                        chat_id=config.CHANNEL_ID,
                        text=f'Лучшая практика <b>{str(data[0])}</b> '
                             f'закончилась')
                await db.post(
                    await queries.update_value(
                        table='best_practice',
                        column_name='over',
                        where_name='id'
                    ),
                    value=True,
                    id=i[0]
                )
    except Exception as error:
        logging.info(f'Schedule error: {error}')


async def check_redis(dp: Dispatcher):
    r = redis.Redis(config.REDIS_HOST,
                    socket_connect_timeout=1)
    try:
        r.ping()
        logging.info('Checking redis connection - OK')
    except (redis.exceptions.ConnectionError,
            redis.exceptions.TimeoutError):
        await dp.bot.send_message(
            chat_id=config.ADMIN_ID,
            text='‼REDIS УПАЛ‼'
        )


async def clear_logs(dp: Dispatcher):
    file = AsyncPath(config.LOG_FILE)
    if await file.is_file():
        async with aiofiles.open(config.LOG_FILE, 'w') as file:
            pass
