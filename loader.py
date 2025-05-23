from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

import config
from utils.db_ops import BotDB

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = RedisStorage2(
    password=config.REDIS_PASSWORD,
    host=config.REDIS_HOST)

job_stores = {
    "default": RedisJobStore(
        jobs_key="dispatched_trips_jobs",
        run_times_key="dispatched_trips_running",
        host=config.REDIS_HOST,
        port=6379,
        password=config.REDIS_PASSWORD
    )
}

dp = Dispatcher(bot, storage=storage)
db = BotDB('../data.db')
scheduler = AsyncIOScheduler()
