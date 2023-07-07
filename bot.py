import asyncio
import logging


from loader import dp, db, bot, scheduler
from best_practice.handlers import register_handlers_best_practice
from kpi.handlers import register_handlers_kpi
from motivation.handlers import register_handlers_motivation
from profile.handlers import register_handlers_profile
from ratings.handlers import register_handlers_ratings
from shop.handlers import register_handlers_shop
from tools.handlers import register_handlers_tools
from users.handlers import register_handlers_users
from utils.jobs import check_bp_start, check_bp_stop

logger = logging.getLogger('bot')
logging.getLogger('apscheduler.executors.default').propagate = False


def set_scheduled_jobs():
    scheduler.add_job(func=check_bp_start,
                      trigger='cron',
                      hour=23,
                      minute=10,
                      timezone='Europe/Moscow',
                      args=(dp,))
    scheduler.add_job(func=check_bp_stop,
                      trigger='cron',
                      hour=23,
                      minute=15,
                      timezone='Europe/Moscow',
                      args=(dp,))


async def start():
    logging.basicConfig(filename='bot_log.log',
                        encoding='UTF-8',
                        filemode='a',
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(name)s - %("
                               "message)s")
    logger.info("Starting bot")

    await db.create_connection()

    register_handlers_users(dp)
    register_handlers_best_practice(dp)
    register_handlers_kpi(dp)
    register_handlers_motivation(dp)
    register_handlers_profile(dp)
    register_handlers_ratings(dp)
    register_handlers_shop(dp)
    register_handlers_tools(dp)

    set_scheduled_jobs()

    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        print('stop')
        await db.close()
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard")
    finally:
        loop.close()
