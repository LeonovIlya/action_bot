"""Модуль конфигурации сообщений для адаптационных задач"""

from utils import keyboards
from typing import Dict, Any, Callable, Awaitable, Optional
from aiogram.types import InlineKeyboardMarkup


class MessageConfig:
    """Конфигурационный класс для настройки сообщений и клавиатур"""

    def __init__(
            self,
            text: Callable[[str, str], str],
            keyboard: Callable[..., Awaitable[InlineKeyboardMarkup]],
            keyboard_args: Callable[[Dict, str], Dict[str, Any]],
            include_link: bool = False,
            link: Optional[str] = None):
        """Инициализирует конфигурацию сообщения"""
        self.text = text
        self.keyboard = keyboard
        self.keyboard_args = keyboard_args
        self.include_link = include_link
        self.link = link


# Конфигурация сообщений по этапам адаптации
ADAPTATION_MESSAGES: Dict[str, MessageConfig] = {
    "date_start_3": MessageConfig(
        text=lambda name, intern: f"{name}, привет! К тебе на стажировку "
                                  f"вышел(-ла) {intern}.",
        keyboard=keyboards.get_adapt_start,
        keyboard_args=lambda record, column: {
            "record_id": record["id"],
            "column_name": column,
            "date_start": record.get(column), },
        include_link=False),
    "date_1week": MessageConfig(
        text=lambda name, intern: f"{name}, привет! Как прошла 1 неделя "
                                  f"работы нашего новичка {intern}?",
        keyboard=keyboards.get_adapt_1week,
        keyboard_args=lambda record, _: {"record_id": record["id"]},
        include_link=False),
    "date_3week": MessageConfig(
        text=lambda name, intern: f"{name}, привет! Спешу напомнить, что в "
                                  f"конце 3 рабочей недели наш новичок {intern}"
                                  f" должен(-на) пройти 'Тест среза знаний'!",
        keyboard=keyboards.get_adapt_3week,
        keyboard_args=lambda record, _: {"record_id": record["id"]},
        include_link=True,
        link='<a href="http://ya.ru/">ССЫЛКА НА ТЕСТ</a>'),
    "date_3week_5": MessageConfig(
        text=lambda name, intern: f"{name}, привет! {intern} прошел(-ла) тест "
                                  f"среза знаний? Не забудь, это важный этап, "
                                  f"чтобы понять, что не хватает из знаний "
                                  f"новичку!",
        keyboard=keyboards.get_adapt_3week_5,
        keyboard_args=lambda record, _: {"record_id": record["id"]},
        include_link=False),
    "date_6week": MessageConfig(
        text=lambda name, intern: f"{name}, привет! Вот и подошла к концу "
                                  f"адаптация {intern}. Уверен, он(она) "
                                  f"прошёл(-ла) все этапы позитивно и уже "
                                  f"показывает результаты. Но помимо нашей "
                                  f"оценки сотрудника, нам важно знать, что он "
                                  f"чувствовал на этапе адаптации. Направляю "
                                  f"ссылку на опрос удовлетворённости.",
        keyboard=keyboards.get_adapt_6week,
        keyboard_args=lambda record, _: {"record_id": record["id"]},
        include_link=True,
        link='<a href="http://ya.ru/">ССЫЛКА НА ОПРОС</a>'),
    "date_6week_3": MessageConfig(
        text=lambda name, intern: f"{name}, привет! Помни, что нам важно мнение"
                                  f" новичка о процессе адаптации. Ты направила"
                                  f" опрос удовлетворённости?",
        keyboard=keyboards.get_adapt_6week_3,
        keyboard_args=lambda record, _: {"record_id": record["id"]},
        include_link=True,
        link='<a href="http://ya.ru/">ССЫЛКА НА ОПРОС</a>')}
