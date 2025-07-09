"""Модуль формирования фоновых задач"""


from .jobs import (check_bp_start, check_bp_stop, check_mp_start,
                        check_mp_stop, clear_logs, check_redis,
                        transfer_gs_to_db, check_adaptation)


def set_scheduled_jobs(scheduler):
    """Добавляет фоновые задачи в планировщик (scheduler)."""
    # Проверка окончания BP
    scheduler.add_job(
        func=check_bp_stop,
        trigger='cron',
        hour=0,
        minute=3)

    # Проверка окончания MP
    scheduler.add_job(
        func=check_mp_stop,
        trigger='cron',
        hour=0,
        minute=4)

    # Проверка начала BP
    scheduler.add_job(
        func=check_bp_start,
        trigger='cron',
        hour=0,
        minute=1)

    # Проверка начала MP
    scheduler.add_job(
        func=check_mp_start,
        trigger='cron',
        hour=0,
        minute=2)

    # Проверка активности Redis
    scheduler.add_job(
        func=check_redis,
        trigger='interval',
        minutes=1)

    # Очистка логов 1 раз в месяц
    scheduler.add_job(
        func=clear_logs,
        trigger='cron',
        day='last')

    # Проверка адаптаций
    scheduler.add_job(
        func=check_adaptation,
        trigger='cron',
        hour=11,
        minute=0)

    # Проверка гугл таблиц
    scheduler.add_job(
        func=transfer_gs_to_db,
        trigger='cron',
        hour=3,
        minute=0)
