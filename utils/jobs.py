import logging
import redis
import aiofiles
from datetime import datetime as dt
from aiopath import AsyncPath
from aiogram import Dispatcher
from typing import Union

import config
from loader import db
from utils import queries


# функция проверки в бд по текущей дате
async def check(name: str, column_name: str, **kwargs) -> Union[list, None]:
    try:
        data = await db.get_all(
            await queries.get_value(
                value='*',
                table=name),
            **kwargs)
        if data:
            for i in data:
                await db.post(
                    await queries.update_value(
                        table=name,
                        column_name=column_name,
                        where_name='id'),
                    value=True,
                    id=i[0])
            return data
        return None
    except Exception as error:
        logging.info('Schedule error: %s', error)


async def get_now() -> dt:
    now = dt.now().date()
    return dt.strptime(str(now), '%Y-%m-%d')


# преобразование datetime в читаемый формат
async def datetime_op(dt_start: str , dt_stop: str) -> tuple:
    datetime_start = dt.strptime(str(dt_start), '%Y-%m-%d %H:%M:%S')
    datetime_stop = dt.strptime(str(dt_stop), '%Y-%m-%d %H:%M:%S')
    start = datetime_start.strftime('%d %B %Y')
    stop = datetime_stop.strftime('%d %B %Y')
    return start, stop


# проверка на начало лучших практик
async def check_bp_start(dp: Dispatcher):
    now = await get_now()
    data = await check(
        name='best_practice',
        column_name='is_active',
        datetime_start=now,
        is_active=False,
        is_over=False)
    if data:
        for i in data:
            start, stop = await datetime_op(i[6], i[7])
            file = AsyncPath(str(i[8]))
            if await file.is_file():
                async with aiofiles.open(file, 'rb') as photo:
                    await dp.bot.send_photo(
                        chat_id=config.CHANNEL_ID,
                        photo=photo,
                        caption='С сегодняшнего дня доступна '
                                'новая практика!\n\n'
                                f'<b>{str(i[2])}</b>\n\n'
                                f'{str(i[3])}\n\n'
                                f'<b>Дата начала:</b>\n'
                                f'{str(start)}\n\n'
                                f'<b>Дата окончания:</b>\n'
                                f'{str(stop)}')
            else:
                await dp.bot.send_message(
                    chat_id=config.CHANNEL_ID,
                    text='С сегодняшнего дня доступна новая '
                         'практика!\n\n'
                         f'<b>{str(i[2])}</b>\n\n'
                         f'{str(i[3])}\n\n'
                         f'<b>Дата начала:</b>\n'
                         f'{str(start)}\n\n'
                         f'<b>Дата окончания:</b>\n'
                         f'{str(stop)}')


# проверка на начало мотивационных программ
async def check_mp_start(dp: Dispatcher):
    now = await get_now()
    data = await check(
        name='mp',
        column_name='is_active',
        datetime_start=now,
        is_active=False,
        is_over=False)
    if data:
        for i in data:
            start, stop = await datetime_op(i[4], i[5])
            await dp.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text='С сегодняшнего дня доступна новая '
                     'Мотивационная программа!\n\n'
                     f'<b>{str(i[1])}</b>\n'
                     f'Для: {str(i[2])}\n'
                     f'Регион: {str(i[3])}\n\n'
                     f'<b>Дата начала:</b>\n'
                     f'{str(start)}\n\n'
                     f'<b>Дата окончания:</b>\n'
                     f'{str(stop)}')


# проверка на окончание лучших практик
async def check_bp_stop(dp: Dispatcher):
    now = await get_now()
    data = await check(
        name='best_practice',
        column_name='is_over',
        datetime_stop=now,
        is_active=True,
        is_over=False)
    if data:
        for i in data:
            await dp.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=f'Лучшая практика <b>{str(i[2])}</b> закончилась!')


# проверка на окончание мотивационных программ
async def check_mp_stop(dp: Dispatcher):
    now = await get_now()
    data = await check(
        name='mp',
        column_name='is_over',
        datetime_stop=now,
        is_active=True,
        is_over=False)
    if data:
        for i in data:
            await dp.bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=f'Мотивационная программа <b>{str(i[1])}</b> '
                     f'для <b>{str(i[2])}</b> '
                     f'в регионе <b>{str(i[3])}</b> закончилась!')


# проверка работы редиса
# async def check_redis(dp: Dispatcher):
#     r = redis.Redis(host=config.REDIS_HOST,
#                     password=config.REDIS_PASSWORD,
#                     socket_connect_timeout=1)
#     try:
#         r.ping()
#         logging.info('Checking redis connection - OK')
#     except (redis.exceptions.ConnectionError,
#             redis.exceptions.TimeoutError):
#         await dp.bot.send_message(
#             chat_id=config.ADMIN_ID,
#             text='‼REDIS УПАЛ‼')


# очистка лог-файла
async def clear_logs(dp: Dispatcher):
    file = AsyncPath(config.LOG_FILE)
    if await file.is_file():
        async with aiofiles.open(file, 'w') as file:
            pass
