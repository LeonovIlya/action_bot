"""Модуль планировщика задач для Telegram-бота"""

import aiofiles
import logging
from datetime import datetime as dt
from aiopath import AsyncPath
from aiogram import Dispatcher
from redis.asyncio import Redis, RedisError
from typing import Optional, List, Tuple

from config import config
from adaptation.date_parser import get_todays_records
from adaptation.sheets_api import GoogleSheetsProcessor
from loader import bot,db
from utils import queries
from utils.adapt_msg import ADAPTATION_MESSAGES, MessageConfig

logger = logging.getLogger("bot")


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
            logger.warning(f"Неизвестный регион: {region}. "
                           f"Используется канал по умолчанию.")
            return config.DEFAULT_CHANNEL_ID


async def check(name: str, column_name: str, **kwargs) -> Optional[List[Tuple]]:
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
            logger.info(
                f"Найдено и обновлено {len(data)} записей в таблице {name}")
            return data
        logger.debug(f"Записей не найдено в таблице {name}")
        return None
    except Exception as e:
        logger.error(f"Ошибка проверки таблицы {name}: {e}",
                     exc_info=True)
        return None


async def datetime_op(dt_start: str, dt_stop: str) -> tuple:
    """Преобразует строки дат в читаемый формат"""
    try:
        datetime_start = dt.strptime(str(dt_start), '%Y-%m-%d %H:%M:%S')
        datetime_stop = dt.strptime(str(dt_stop), '%Y-%m-%d %H:%M:%S')
        return (datetime_start.strftime('%d %B %Y'),
                datetime_stop.strftime('%d %B %Y'))
    except ValueError as e:
        logger.error(f"Ошибка преобразования дат: {e}")
        return "Неверная дата", "Неверная дата"


# проверка на начало лучших практик
async def check_bp_start():
    """Проверяет начало новых лучших практик и отправляет уведомления"""
    logger.info("Проверка начала новых лучших практик")
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
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=photo,
                            caption=message_text)
                else:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=message_text)
    except Exception as error:
        logger.error('Ошибка при запуске BP: %s', error,
                     exc_info=True)


# проверка на начало мотивационных программ
async def check_mp_start():
    """Проверяет начало новых мотивационных программ и отправляет уведомления"""
    logger.info("Проверка начала мотивационных программ")
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
                await bot.send_message(
                    chat_id=chat_id,
                    text=message_text)
    except Exception as error:
        logger.error('Ошибка при запуске MP: %s', error,
                     exc_info=True)


# проверка на окончание лучших практик
async def check_bp_stop():
    """Проверяет завершение лучших практик и отправляет уведомления"""
    logger.info("Проверка завершения лучших практик")
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
                await bot.send_message(
                    chat_id=chat_id,
                    text=f'Лучшая практика <b>{str(i[2])}</b> закончилась!')
    except Exception as error:
        logger.error('Ошибка при завершении BP: %s', error,
                     exc_info=True)


# проверка на окончание мотивационных программ
async def check_mp_stop():
    """Проверяет завершение мотивационных программ и отправляет уведомления"""
    logger.info("Проверка завершения мотивационных программ")
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
                await bot.send_message(
                    chat_id=chat_id,
                    text=f'Мотивационная программа <b>{str(i[1])}</b> '
                         f'для <b>{str(i[2])}</b> '
                         f'в регионе <b>{str(i[3])}</b> закончилась!')
    except Exception as error:
        logger.error('Ошибка при завершении MP: %s', error,
                     exc_info=True)


async def transfer_gs_to_db():
    """Переносит данные из Google Sheets в базу данных"""
    logger.info("Начало переноса данных из Google Sheets в БД")
    try:
        processor = GoogleSheetsProcessor()
        await processor.all_data_to_db()
        logger.info("Успешное завершение переноса GS → DB")
    except Exception as error:
        logger.error("Ошибка переноса GS → DB: %s", error,
                     exc_info=True)


async def check_adaptation():
    """Проверяет адаптационные задачи на сегодня и отправляет уведомления"""
    logger.info("Проверка адаптационных задач")
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
                    await send_message_to_mentor(mentor, record, cnfg,
                                                 column)
                else:
                    await notify_cm(mentor)
    except Exception as error:
        logger.error("Ошибка при проверке адаптации: %s", error,
                     exc_info=True)


async def send_message_to_mentor(
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
        await bot.send_message(
            chat_id=mentor[0],
            text=message_text,
            reply_markup=keyboard)
        if cnfg.include_link:
            await bot.send_message(chat_id=mentor[0], text=cnfg.link)
    except Exception as error:
        logger.error(f"Ошибка отправки сообщения ментору: {error}",
                     exc_info=True)


async def notify_cm(mentor: tuple):
    """Уведомляет CityManager о проблемах с авторизацией ментора"""
    try:
        cm_tg_id = await db.get_one(
            await queries.get_value("tg_id", "users"),
            username=mentor[1])
        if cm_tg_id and cm_tg_id[0]:
            await bot.send_message(
                chat_id=cm_tg_id[0],
                text=f"Ваш сотрудник {mentor[2]} не авторизован в боте. "
                     f"Обновление информации по адаптации его стажеров "
                     f"невозможно.")
    except Exception as error:
        logger.error(f"Ошибка уведомления CityManager: {error}",
                     exc_info=True)


async def check_redis():
    """Проверяет работоспособность Redis"""
    r = Redis(host=config.REDIS_HOST,
              password=config.REDIS_PASSWORD,
              socket_connect_timeout=1)
    try:
        await r.ping()
    except RedisError:
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text='‼REDIS УПАЛ‼')
        logger.error('Проверка подключения к Redis — провалена')


async def clear_logs():
    """Очищает файл логов"""
    logger.info("Очистка файла логов")
    try:
        file = AsyncPath(config.LOG_FILE)
        if await file.is_file():
            async with aiofiles.open(file, 'w') as f:
                await f.write('')
            logger.info("Файл логов успешно очищен")
        else:
            logger.warning("Файл логов не найден")
    except Exception as error:
        logger.error('Ошибка очистки логов: %s', error,
                     exc_info=True)
