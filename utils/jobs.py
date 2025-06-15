"""Модуль планировщика задач для Telegram-бота"""

import aiofiles
import logging
from datetime import datetime as dt
from aiopath import AsyncPath
from aiogram import Dispatcher
from redis.asyncio import Redis, RedisError
from typing import Optional, List, Tuple

import config
from adaptation.date_parser import get_todays_records
from adaptation.sheets_api import GoogleSheetsProcessor
from loader import db
from utils import keyboards, queries
from utils.adapt_msg import ADAPTATION_MESSAGES, MessageConfig


logger = logging.getLogger("bot")


async def check(name: str, column_name: str, **kwargs) -> Optional[
    List[Tuple]]:
    """Проверяет записи в БД по текущей дате"""
    try:
        data = await db.get_all(
            await queries.get_value(value='*', table=name),
            **kwargs)
        if data:
            for record in data:
                await db.post(
                    await queries.update_value(
                        table=name,
                        column_name=column_name,
                        where_name='id'),
                    value=True,
                    id=record[0])
            logger.info(f"Found and updated {len(data)} records in {name}")
            return data
        logger.debug(f"No matching records found in {name}")
        return None
    except Exception as e:
        logger.error(f"Database check error in table {name}: {e}",
                     exc_info=True)
        return None


async def get_now() -> dt:
    """Возвращает текущую дату в формате datetime"""
    now = dt.now().date()
    return dt.strptime(str(now), '%Y-%m-%d')


async def get_region_channel(region: str) -> str:
    """Возвращает ID канала для региона"""
    match region:
        case 'Moscow':
            return config.MOSCOW_CHANNEL_ID
        case 'Center':
            return config.CENTER_CHANNEL_ID
        case 'North':
            return config.NORTH_CHANNEL_ID
        case _:
            logger.warning(f"Unknown region: {region}. Using default channel.")
            return config.DEFAULT_CHANNEL_ID


# преобразование datetime в читаемый формат
async def datetime_op(dt_start: str, dt_stop: str) -> tuple:
    """Преобразует строки дат в читаемый формат"""
    try:
        datetime_start = dt.strptime(str(dt_start), '%Y-%m-%d %H:%M:%S')
        datetime_stop = dt.strptime(str(dt_stop), '%Y-%m-%d %H:%M:%S')
        return (datetime_start.strftime('%d %B %Y'),
                datetime_stop.strftime('%d %B %Y'))
    except ValueError as e:
        logger.error(f"Date parsing error: {e}")
        return "Invalid date", "Invalid date"


# проверка на начало лучших практик
async def check_bp_start(dp: Dispatcher):
    """Проверяет начало новых лучших практик и отправляет уведомления"""
    logger.info("Checking for new best practices")
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
                message_text = (
                    'С сегодняшнего дня доступна новая практика!\n\n'
                    f'<b>{str(i[2])}</b>\n\n'
                    f'{str(i[3])}\n\n'
                    f'<b>Дата начала:</b>\n{start}\n\n'
                    f'<b>Дата окончания:</b>\n{stop}')
                if await file.is_file():
                    async with aiofiles.open(file, 'rb') as photo:
                        await dp.bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=message_text)
                else:
                    await dp.bot.send_message(
                        chat_id=chat_id,
                        text=message_text)
    except Exception as error:
        logger.error('Schedule error for BP start: %s', error, exc_info=True)


# проверка на начало мотивационных программ
async def check_mp_start(dp: Dispatcher):
    """Проверяет начало новых мотивационных программ и отправляет уведомления"""
    logger.info("Checking for new motivational programs")
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
                message_text = (
                    'С сегодняшнего дня доступна новая '
                    'мотивационная программа!\n\n'
                    f'<b>{str(i[1])}</b>\n'
                    f'Для: {str(i[2])}\n'
                    f'Регион: {str(i[3])}\n\n'
                    f'<b>Дата начала:</b>\n{start}\n\n'
                    f'<b>Дата окончания:</b>\n{stop}')
                await dp.bot.send_message(
                    chat_id=chat_id,
                    text=message_text)
    except Exception as error:
        logger.error('Schedule error for MP start: %s', error, exc_info=True)


# проверка на окончание лучших практик
async def check_bp_stop(dp: Dispatcher):
    """Проверяет завершение лучших практик и отправляет уведомления"""
    logger.info("Checking for finished best practices")
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
        logger.error('Schedule error for BP stop: %s', error, exc_info=True)


# проверка на окончание мотивационных программ
async def check_mp_stop(dp: Dispatcher):
    """Проверяет завершение мотивационных программ и отправляет уведомления"""
    logger.info("Checking for finished motivational programs")
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
        logger.error('Schedule error for MP stop: %s', error, exc_info=True)


async def transfer_gs_to_db(dp: Dispatcher):
    """Переносит данные из Google Sheets в базу данных"""
    logger.info("Starting GS to DB transfer")
    try:
        processor = GoogleSheetsProcessor()
        await processor.all_data_to_db()
        logger.info("Successfully completed GS to DB transfer")
    except Exception as error:
        logger.error("GS to DB transfer failed: %s", error, exc_info=True)


async def check_adaptation(dp: Dispatcher):
    """Проверяет адаптационные задачи на сегодня и отправляет уведомления"""
    logger.info("Checking adaptation tasks")
    try:
        today = dt.strftime(dt.now().date(), "%d.%m.%Y")
        data = await get_todays_records("adaptation", today)
        if not data:
            return
        for record in data:
            for column in record.get("matched_columns", []):
                cnfg = ADAPTATION_MESSAGES.get(column)
                if not cnfg:
                    continue
                mentor = await db.get_one(
                    await queries.get_value(
                        value="tg_id, citimanager, username",
                        table="users"),
                    ter_num=record.get("mentor_ter_num"))
                if not mentor:
                    continue
                if mentor[0] != 0:
                    await send_message_to_mentor(dp, mentor, record, cnfg, column)
                else:
                    await notify_cm(dp, mentor)
    except Exception as error:
        logger.error("Check adaptation error: %s", error, exc_info=True)


async def send_message_to_mentor(
    dp: Dispatcher,
    mentor: tuple,
    record: dict,
    cnfg: MessageConfig,
    column: str):
    """Отправляет сообщение ментору о задаче адаптации"""
    try:
        mentor_name = record.get("mentor_name").split(" ")[1]
        intern_name = record.get("intern_name")
        message_text = cnfg.text(mentor_name, intern_name)
        args = cnfg.keyboard_args(record, column)
        keyboard = await cnfg.keyboard(**args)
        await dp.bot.send_message(
            chat_id=mentor[0],
            text=message_text,
            reply_markup=keyboard)
        if cnfg.include_link:
            await dp.bot.send_message(chat_id=mentor[0], text=cnfg.link)
    except Exception as error:
        logger.error(f"Failed to send message to mentor: {error}",
                     exc_info=True)


async def notify_cm(dp: Dispatcher, mentor: tuple):
    """Уведомляет CityManager о проблемах с авторизацией ментора"""
    try:
        cm_tg_id = await db.get_one(
            await queries.get_value("tg_id", "users"),
            username=mentor[1])
        if cm_tg_id and cm_tg_id[0]:
            await dp.bot.send_message(
                chat_id=cm_tg_id[0],
                text=f"Ваш сотрудник {mentor[2]} не авторизован в боте. Обновление информации по адаптации его стажеров невозможно.")
    except Exception as error:
        logger.error(f"Failed to notify CM: {error}", exc_info=True)



async def check_redis(dp: Dispatcher):
    """Проверяет работоспособность Redis"""
    r = Redis(host=config.REDIS_HOST,
              password=config.REDIS_PASSWORD,
              socket_connect_timeout=1)
    try:
        await r.ping()
    except RedisError:
        await dp.bot.send_message(
            chat_id=config.ADMIN_ID,
            text='‼REDIS УПАЛ‼')
        logger.error('Checking redis connection - FAIL')



async def clear_logs(dp: Dispatcher):
    """Очищает файл логов"""
    logger.info("Clearing log file")
    try:
        file = AsyncPath(config.LOG_FILE)
        if await file.is_file():
            async with aiofiles.open(file, 'w') as f:
                await f.write('')
            logger.info("Log file cleared successfully")
        else:
            logger.warning("Log file does not exist")
    except Exception as error:
        logger.error('Failed to clear logs: %s', error, exc_info=True)
