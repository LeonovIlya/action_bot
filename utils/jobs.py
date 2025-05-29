import logging
import aiofiles
from datetime import datetime as dt
from aiopath import AsyncPath
from aiogram import Dispatcher
from redis.asyncio import Redis, RedisError

import config
from adaptation.date_parser import get_todays_records
from utils.keyboards import AsyncAdaptationKeyboards
from loader import db
from utils import queries

from pprint import pp


# функция проверки в бд по текущей дате
async def check(name: str, column_name: str, **kwargs) -> list | None:
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


async def get_now() -> dt:
    now = dt.now().date()
    return dt.strptime(str(now), '%Y-%m-%d')


async def get_region_channel(region: str) -> str:
    match region:
        case 'Moscow':
            return config.MOSCOW_CHANNEL_ID
        case 'Center':
            return config.CENTER_CHANNEL_ID
        case 'North':
            return config.NORTH_CHANNEL_ID


# преобразование datetime в читаемый формат
async def datetime_op(dt_start: str , dt_stop: str) -> tuple:
    datetime_start = dt.strptime(str(dt_start), '%Y-%m-%d %H:%M:%S')
    datetime_stop = dt.strptime(str(dt_stop), '%Y-%m-%d %H:%M:%S')
    start = datetime_start.strftime('%d %B %Y')
    stop = datetime_stop.strftime('%d %B %Y')
    return start, stop


# проверка на начало лучших практик
async def check_bp_start(dp: Dispatcher):
    try:
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
                chat_id = await get_region_channel(i[1])
                file = AsyncPath(str(i[8]))
                if await file.is_file():
                    async with aiofiles.open(file, 'rb') as photo:
                        await dp.bot.send_photo(
                            chat_id=chat_id,
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
                        chat_id=chat_id,
                        text='С сегодняшнего дня доступна новая '
                             'практика!\n\n'
                             f'<b>{str(i[2])}</b>\n\n'
                             f'{str(i[3])}\n\n'
                             f'<b>Дата начала:</b>\n'
                             f'{str(start)}\n\n'
                             f'<b>Дата окончания:</b>\n'
                             f'{str(stop)}')
    except Exception as error:
        logging.error('Schedule error: %s', error)


# проверка на начало мотивационных программ
async def check_mp_start(dp: Dispatcher):
    try:
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
                chat_id = await get_region_channel(i[3])
                await dp.bot.send_message(
                    chat_id=chat_id,
                    text='С сегодняшнего дня доступна новая '
                         'Мотивационная программа!\n\n'
                         f'<b>{str(i[1])}</b>\n'
                         f'Для: {str(i[2])}\n'
                         f'Регион: {str(i[3])}\n\n'
                         f'<b>Дата начала:</b>\n'
                         f'{str(start)}\n\n'
                         f'<b>Дата окончания:</b>\n'
                         f'{str(stop)}')
    except Exception as error:
        logging.error('Schedule error: %s', error)


# проверка на окончание лучших практик
async def check_bp_stop(dp: Dispatcher):
    try:
        now = await get_now()
        data = await check(
            name='best_practice',
            column_name='is_over',
            datetime_stop=now,
            is_active=True,
            is_over=False)
        if data:
            for i in data:
                chat_id = await get_region_channel(i[1])
                await dp.bot.send_message(
                    chat_id=chat_id,
                    text=f'Лучшая практика <b>{str(i[2])}</b> закончилась!')
    except Exception as error:
        logging.error('Schedule error: %s', error)


# проверка на окончание мотивационных программ
async def check_mp_stop(dp: Dispatcher):
    try:
        now = await get_now()
        data = await check(
            name='mp',
            column_name='is_over',
            datetime_stop=now,
            is_active=True,
            is_over=False)
        if data:
            for i in data:
                chat_id = await get_region_channel(i[3])
                await dp.bot.send_message(
                    chat_id=chat_id,
                    text=f'Мотивационная программа <b>{str(i[1])}</b> '
                         f'для <b>{str(i[2])}</b> '
                         f'в регионе <b>{str(i[3])}</b> закончилась!')
    except Exception as error:
        logging.error('Schedule error: %s', error)


async def check_adaptation(dp: Dispatcher):
    try:
        print('check_adaptation...')
        today = await get_now()
        data = await get_todays_records('adaptation', today)
        if data:
            for i in data:
                pp(i)
                for k in i.get('matched_columns'):
                    match k:
                        case 'date_start_3':
                            mentor_tg_id = await db.get_one(await
                                                              queries.get_value('tg_id', 'users'), ter_num=i.get('mentor_ter_num'))
                            mentor_name = i.get('mentor_name').split(' ')[1]
                            keyboard = await (
                                AsyncAdaptationKeyboards.get_adapt_start(i['id']))
                            await dp.bot.send_message(
                                chat_id=mentor_tg_id[0],
                                text=f"{mentor_name}, привет! К тебе на "
                                     f"стажировку вышел(-ла)"
                                     f" {i.get('intern_name')}.",
                            reply_markup=keyboard)

                        case 'date_1day':
                            pass
                        case 'date_1week':
                            pass
                        case 'date_2week':
                            pass
                        case 'date_3week':
                            pass
                        case 'date_6week':
                            pass
                        case 'date_lastday':
                            pass


    except Exception as error:
        logging.error('Check adaptation error: %s', error)
# проверка работы редиса
async def check_redis(dp: Dispatcher):
    r = Redis(host=config.REDIS_HOST,
                    password=config.REDIS_PASSWORD,
                    socket_connect_timeout=1)
    try:
        await r.ping()
    except RedisError:
        await dp.bot.send_message(
            chat_id=config.ADMIN_ID,
            text='‼REDIS УПАЛ‼')
        logging.error('Checking redis connection - FAIL')


# очистка лог-файла
async def clear_logs(dp: Dispatcher):
    try:
        file = AsyncPath(config.LOG_FILE)
        if await file.is_file():
            async with aiofiles.open(file, 'w') as file:
                pass
    except Exception as error:
        logging.error('Clear logs fail: %s', error)
