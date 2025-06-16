import asyncio
import logging
from loader import dp, scheduler, bot, db
from utils.jobs import check_adaptation, transfer_gs_to_db
from adaptation.handler import register_handlers_adaptation
from config import config

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
    scheduler.add_job(func=check_adaptation,
                      trigger='interval',
                      seconds=10)
    scheduler.add_job(func=transfer_gs_to_db,
                      trigger='interval',
                      seconds=60)


async def main():
    logger.info('>>> Starting bot')
    await db.create_connection()
    register_handlers_adaptation(dp)
    set_scheduled_jobs()
    scheduler.start()
    try:
        await dp.start_polling()
    finally:
        await on_shutdown()


async def on_shutdown():
    logger.info('>>> Bot has been stopped!')
    dp.stop_polling()
    await db.close_connection()
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.session.close()


if __name__ == '__main__':
    try:
        logger.info("Бот запущен")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info(">>> Бот остановлен вручную")
