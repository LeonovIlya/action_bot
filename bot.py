"""Основной модуль запуска Telegram-бота."""

import asyncio
import logging

# Импорты из проекта
from config import config
from loader import dp, db, bot, scheduler

# Обработчики различных модулей
from adaptation.handler import register_handlers_adaptation
from admin_manager.handler import register_handlers_admin_manager
from best_practice.handlers import register_handlers_best_practice
from kpi.handlers import register_handlers_kpi
from motivation.handlers import register_handlers_motivation
from profile.handlers import register_handlers_profile
from ratings.handlers import register_handlers_ratings
from shop.handlers import register_handlers_shop
from tools.handlers import register_handlers_tools
from users.handlers import register_handlers_users
from utils.schedule import set_scheduled_jobs

# === Настройка логирования ===
logger = logging.getLogger('bot')

# Отключение передачи логов от apscheduler наверх
logging.getLogger('apscheduler.executors.default').propagate = False

# Базовая настройка логирования
logging.basicConfig(
    filename=config.LOG_FILE,
    encoding='UTF-8',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


async def main():
    """Запускает основную логику бота: подключение к БД, регистрация хэндлеров
     и запуск polling."""
    logger.info('>>> Starting bot')
    try:
        # Подключение к базе данных
        await db.create_connection()

        # Регистрация всех обработчиков
        register_handlers_admin_manager(dp)
        register_handlers_users(dp)
        register_handlers_best_practice(dp)
        register_handlers_kpi(dp)
        register_handlers_motivation(dp)
        register_handlers_profile(dp)
        register_handlers_ratings(dp)
        register_handlers_shop(dp)
        register_handlers_tools(dp)
        register_handlers_adaptation(dp)

        # Назначение фоновых задач
        set_scheduled_jobs(scheduler)
        logger.info("Фоновые задачи успешно добавлены")
        scheduler.start()

        # Запуск polling
        await dp.start_polling()
    finally:
        await on_shutdown()


async def on_shutdown():
    """Выполняет корректное завершение работы бота."""
    logger.info('>>> Bot has been stopped!')

    # Остановка опроса серверов Telegram
    dp.stop_polling()

    # Закрытие соединения с БД
    await db.close_connection()

    # Закрытие хранилища состояний
    await dp.storage.close()
    await dp.storage.wait_closed()

    # Закрытие сессии бота
    await bot.session.close()


if __name__ == '__main__':
    try:
        logger.info("Бот запущен")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info(">>> Бот остановлен вручную")
