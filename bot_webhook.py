import logging
from aiogram.utils.executor import start_webhook

from config import config
from loader import dp, db, bot, scheduler
from best_practice.handlers import register_handlers_best_practice
from kpi.handlers import register_handlers_kpi
from motivation.handlers import register_handlers_motivation
from profile.handlers import register_handlers_profile
from ratings.handlers import register_handlers_ratings
from shop.handlers import register_handlers_shop
from tools.handlers import register_handlers_tools
from users.handlers import register_handlers_users
from utils.jobs import check_bp_start, check_bp_stop, check_redis, clear_logs
from utils.throttling import ThrottlingMiddleware

logger = logging.getLogger('bot')
logging.getLogger('apscheduler.executors.default').propagate = False

WEBHOOK_HOST = ''
WEBHOOK_PATH = ''
WEBAPP_HOST = '127.0.0.1'
WEBAPP_PORT = 3001
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'


def set_scheduled_jobs():
    scheduler.add_job(func=check_bp_stop,
                      trigger='interval',
                      hours=1,
                      args=(dp,))
    scheduler.add_job(func=check_bp_start,
                      trigger='interval',
                      hours=1,
                      args=(dp,))
    scheduler.add_job(func=check_redis,
                      trigger='interval',
                      minutes=1,
                      args=(dp,))
    scheduler.add_job(func=clear_logs,
                      trigger='interval',
                      days=30,
                      args=(dp,))


def setup_middlewares(dp):
    dp.middleware.setup(ThrottlingMiddleware())


async def on_startup(dp):
    logging.basicConfig(filename=config.LOG_FILE,
                        encoding='UTF-8',
                        filemode='a',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(name)s - %('
                               'message)s')
    logger.info('Starting bot...')
    await bot.set_webhook(WEBHOOK_URL)
    await db.create_connection()
    register_handlers_users(dp)
    register_handlers_best_practice(dp)
    register_handlers_kpi(dp)
    register_handlers_motivation(dp)
    register_handlers_profile(dp)
    register_handlers_ratings(dp)
    register_handlers_shop(dp)
    register_handlers_tools(dp)
    setup_middlewares(dp)
    set_scheduled_jobs()
    scheduler.start()


async def on_shutdown(dp):
    logger.info('Stoping bot...')
    await bot.delete_webhook()
    await db.close()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
