"""Модуль инициализации компонентов бота."""

import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

from config import config
from utils.db_ops import BotDB

logger = logging.getLogger('bot')

# ====== Инициализация бота ======
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# ====== Настройка FSM Storage ======
storage = RedisStorage2(
    host=config.REDIS_HOST,
    password=config.REDIS_PASSWORD or None,
    port=6379,
    db=0)

# ====== Диспетчер ======
dp = Dispatcher(bot, storage=storage)

# ====== Работа с БД ======
async def init_db():
    """Асинхронная инициализация соединения с базой данных."""
    logger.info("Инициализация подключения к БД...")
    db_init = BotDB(config.DB_FILE)
    try:
        await db_init.create_connection()
        logger.info("Подключение к БД установлено")
        return db_init
    except Exception as e:
        logger.error(f"Не удалось подключиться к БД: {e}")
        raise

db = asyncio.run(init_db())

# ====== Планировщик задач ======
job_stores = {'default': RedisJobStore(
    jobs_key="dispatched_trips_jobs",
    run_times_key="dispatched_trips_running",
    host=config.REDIS_HOST,
    port=6379,
    password=config.REDIS_PASSWORD)}

scheduler = AsyncIOScheduler(jobstores=job_stores)
