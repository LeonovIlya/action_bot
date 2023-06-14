import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from loader import dp, db, bot
from planograms.handlers import register_handlers_planogram
from users.handlers import register_handlers_users


logger = logging.getLogger('bot')


async def start():
    logging.basicConfig(filename='bot_log.log',
                        filemode='a',
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(name)s - %("
                               "message)s")
    logger.info("Starting bot")

    await db.create_connection()
    await db.create_table()

    register_handlers_planogram(dp)
    register_handlers_users(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(start())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
