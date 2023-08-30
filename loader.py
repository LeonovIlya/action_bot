from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from utils.db_ops import BotDB

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()

# storage = RedisStorage2(
#     password=config.REDIS_PASSWORD,
#     host=config.REDIS_HOST)

dp = Dispatcher(bot, storage=storage)
db = BotDB('data.db')
scheduler = AsyncIOScheduler()
