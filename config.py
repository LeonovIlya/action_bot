"""Модуль конфигурации телеграм-бота."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Класс настроек приложения."""
    # Telegram Bot
    BOT_TOKEN: str = Field(..., description="Токен Telegram-бота")

    # Google Sheets API
    G_API_FILE: str = Field(..., description="Путь к JSON-файлу сервисного "
                                             "аккаунта Google")
    G_API_EMAIL: str = Field(..., description="Email сервисного аккаунта "
                                              "Google")
    G_API_LINK: str = Field(..., description="Ссылка на Google Таблицу")
    G_TEST_LINK: str = Field(..., description="Ссылка на Тест среза знаний")
    G_SURVEY_LINK: str = Field(..., description="Ссылка на Опрос "
                                                "удовлетворенности")

    # База данных
    DB_FILE: str = Field(..., description="Путь к SQLite базе данных")

    # Логирование
    LOG_FILE: str = Field(..., description="Файл для записи логов")

    # Redis
    REDIS_HOST: str = Field("localhost", description="Хост Redis сервера")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Пароль от Redis "
                                                            "(если есть)")

    # Каналы Telegram
    MOSCOW_CHANNEL_ID: str = Field(..., description="ID канала Москва")
    CENTER_CHANNEL_ID: str = Field(..., description="ID канала Центр")
    NORTH_CHANNEL_ID: str = Field(..., description="ID канала Север")
    DEFAULT_CHANNEL_ID: str = Field(..., description="ID канала по умолчанию")

    # Администратор
    ADMIN_ID: int = Field(..., description="ID администратора бота")

    # Ограничения скорости
    RATE_LIMIT: float = Field(0.5, description="Ограничение запросов в "
                                               "секунду")

    class Config:
        """Конфигурационный класс для настройки загрузки переменных
        окружения."""
        env_file = ".env"
        env_file_encoding = "utf-8"


# Создаём экземпляр настроек
config = Settings()
