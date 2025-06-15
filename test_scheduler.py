import asyncio
import logging
from loader import dp, scheduler, bot, db
from utils.jobs import check_adaptation, transfer_gs_to_db
from adaptation.handler import register_handlers_adaptation
import config

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
                      seconds=10,
                      args=(dp,))
    scheduler.add_job(func=transfer_gs_to_db,
                      trigger='interval',
                      seconds=60,
                      args=(dp,))


async def main():
    logger.info('>>> Starting bot')
    await db.create_connection()
    set_scheduled_jobs()
    scheduler.start()
    register_handlers_adaptation(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
