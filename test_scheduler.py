import asyncio
from loader import dp, scheduler, bot, db
from utils.jobs import check_adaptation
from adaptation.handler import register_handlers_adaptation



def set_scheduled_jobs():
    scheduler.add_job(func=check_adaptation,
                      trigger='interval',
                      seconds=10,
                      args=(dp,))


async def main():
    await db.create_connection()
    set_scheduled_jobs()
    scheduler.start()
    register_handlers_adaptation(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
