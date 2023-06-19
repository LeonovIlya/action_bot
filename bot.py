import asyncio
import logging

from loader import dp, db, bot
from best_practice.handlers import register_handlers_best_practice
from kpi.handlers import register_handlers_kpi
from ratings.handlers import register_handlers_ratings
from tools.handlers import register_handlers_planogram
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

    register_handlers_best_practice(dp)
    register_handlers_kpi(dp)
    register_handlers_planogram(dp)
    register_handlers_ratings(dp)
    register_handlers_users(dp)
    register_handlers_ratings(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(start())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
