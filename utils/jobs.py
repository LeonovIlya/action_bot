import aiofiles
from aiogram import Dispatcher
from aiopath import AsyncPath
from datetime import datetime as dt

import config
from loader import db
from utils import keyboards, queries


async def check_bp_start(dp: Dispatcher):
    now = dt.now().date()
    now = dt.strptime(str(now), '%Y-%m-%d')
    bp = await db.get_all(
        await queries.get_value(
            value='id',
            table='best_practice'
        ),
        datetime_start=now
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
                        caption='ВНИМАНИЕ! С сегодняшнего дня доступна новая '
                                'практика!\n\n'
                                f'<b>{str(data[0])}</b>\n\n'
                                f'{str(data[1])}\n\n'
                                f'<b>Дата начала:</b>\n'
                                f'{str(start)}\n\n'
                                f'<b>Дата окончания:</b>\n'
                                f'{str(stop)}')
            else:
                await dp.bot.send_message(
                    text='ВНИМАНИЕ! С сегодняшнего дня доступна новая '
                         'практика!\n\n'
                         f'<b>{str(data[0])}</b>\n\n'
                         f'{str(data[1])}\n\n'
                         f'<b>Дата начала:</b>\n'
                         f'{str(start)}\n\n'
                         f'<b>Дата окончания:</b>\n'
                         f'{str(stop)}')


async def check_bp_stop(dp: Dispatcher):
    now = dt.now().date()
    now = dt.strptime(str(now), '%Y-%m-%d')
    bp = await db.get_all(
        await queries.get_value(
            value='id',
            table='best_practice'
        ),
        datetime_stop=now
    )
