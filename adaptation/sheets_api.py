import asyncio
from gspread_asyncio import AsyncioGspreadClientManager, \
    AsyncioGspreadSpreadsheet, AsyncioGspreadWorksheet
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional
from config import G_API_FILE, G_API_LINK


CREDENTIALS_PATH = G_API_FILE
SPREADSHEET_URL = G_API_LINK


class AsyncGoogleSheetsClient:
    """Асинхронный клиент для работы с Google Sheets API"""

    def __init__(self, credentials_path: str):
        """
        Инициализация клиента

        Args:
            credentials_path (str): Путь к JSON-файлу с учетными данными сервисного аккаунта
        """
        self.credentials_path = credentials_path
        self.client_manager = AsyncioGspreadClientManager(self._authorize)
        self.spreadsheet: Optional[AsyncioGspreadSpreadsheet] = None

    def _authorize(self):
        """Авторизация с использованием сервисного аккаунта"""
        return ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_path,
            [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )

    async def connect(self, spreadsheet_url: str) -> None:
        """
        Подключение к таблице по URL

        Args:
            spreadsheet_url (str): Полный URL Google Sheets таблицы

        Raises:
            ValueError: Если не удалось подключиться к таблице
        """
        try:
            agc = await self.client_manager.authorize()
            self.spreadsheet = await agc.open_by_url(spreadsheet_url)
        except Exception as e:
            raise ValueError(f"Ошибка подключения к таблице: {str(e)}")

    async def _get_worksheet(self,
                             worksheet_index: int = 0) -> AsyncioGspreadWorksheet:
        """
        Получение объекта листа

        Args:
            worksheet_index (int): Индекс листа (по умолчанию 0)

        Returns:
            AsyncioGspreadWorksheet: Объект листа

        Raises:
            RuntimeError: Если нет подключения к таблице
        """
        if not self.spreadsheet:
            raise RuntimeError(
                "Не установлено подключение к таблице. Вызовите метод connect()")

        try:
            return await self.spreadsheet.get_worksheet(worksheet_index)
        except Exception as e:
            raise ValueError(
                f"Ошибка получения листа {worksheet_index}: {str(e)}")

    async def get_column_values(self, worksheet_index: int = 0,
                                column: str = "E", start_row: int = 3) -> list[
        str]:
        """
        Получение значений столбца до первой пустой ячейки

        Args:
            worksheet_index (int): Индекс листа (по умолчанию 0)
            column (str): Буква столбца (по умолчанию "E")
            start_row (int): Начальная строка (по умолчанию 3)

        Returns:
            List[str]: Список значений столбца

        Raises:
            ValueError: Если не удалось получить значения
        """
        worksheet = await self._get_worksheet(worksheet_index)
        values = []
        current_row = start_row

        try:
            while True:
                cell_address = f"{column}{current_row}"
                cell = await worksheet.acell(cell_address)

                if not cell.value:
                    break

                values.append(cell.value)
                current_row += 1

            return values
        except Exception as e:
            raise ValueError(f"Ошибка чтения столбца {column}: {str(e)}")


async def main():
    # Инициализация клиента
    sheets_client = AsyncGoogleSheetsClient(CREDENTIALS_PATH)

    try:
        # Подключение к таблице
        await sheets_client.connect(SPREADSHEET_URL)

        # Получение значений столбца E начиная с E3
        values = await sheets_client.get_column_values(column="E", start_row=3)
        print(f"Значения столбца E (начиная с E3): {values}")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())