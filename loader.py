from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from utils.db_ops import BotDB

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = RedisStorage2()

dp = Dispatcher(bot, storage=storage)
db = BotDB('data.db')
scheduler = AsyncIOScheduler()
