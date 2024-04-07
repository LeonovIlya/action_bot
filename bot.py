import asyncio
import logging

import config
from loader import dp, db, bot, scheduler
from admin_manager.handler import register_handlers_admin_manager
from best_practice.handlers import register_handlers_best_practice
from kpi.handlers import register_handlers_kpi
from motivation.handlers import register_handlers_motivation
from profile.handlers import register_handlers_profile
from ratings.handlers import register_handlers_ratings
from shop.handlers import register_handlers_shop
from tools.handlers import register_handlers_tools
from users.handlers import register_handlers_users
from utils.jobs import check_bp_start, check_bp_stop, check_mp_start, \
    check_mp_stop, clear_logs, check_redis

logger = logging.getLogger('bot')
# отключение логов apscheduler
logging.getLogger('apscheduler.executors.default').propagate = False
logging.basicConfig(filename=config.LOG_FILE,
                    encoding='UTF-8',
                    filemode='a',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %('
                           'message)s')


def set_scheduled_jobs():
    scheduler.add_job(func=check_bp_stop,
                      trigger='cron',
                      hour=0,
                      minute=3,
                      args=(dp,))
    scheduler.add_job(func=check_mp_stop,
                      trigger='cron',
                      hour=0,
                      minute=4,
                      args=(dp,))
    scheduler.add_job(func=check_bp_start,
                      trigger='cron',
                      hour=0,
                      minute=1,
                      args=(dp,))
    scheduler.add_job(func=check_mp_start,
                      trigger='cron',
                      hour=0,
                      minute=2,
                      args=(dp,))
    scheduler.add_job(func=check_redis,
                      trigger='interval',
                      minutes=1,
                      args=(dp,))
    scheduler.add_job(func=clear_logs,
                      trigger='cron',
                      year='*',
                      month='*',
                      day='last',
                      args=(dp,))


async def main():
    logger.info('>>> Starting bot')
    await db.create_connection()
    register_handlers_admin_manager(dp)
    register_handlers_users(dp)
    register_handlers_best_practice(dp)
    register_handlers_kpi(dp)
    register_handlers_motivation(dp)
    register_handlers_profile(dp)
    register_handlers_ratings(dp)
    register_handlers_shop(dp)
    register_handlers_tools(dp)
    set_scheduled_jobs()
    scheduler.start()
    await dp.start_polling(bot)


async def on_shutdown():
    dp.stop_polling()
    await db.close()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info('>>> Bot has been stopped!')
    finally:
        loop.close()
