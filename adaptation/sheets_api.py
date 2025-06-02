"""Модуль для работы с Google API"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Union
from gspread_asyncio import AsyncioGspreadClientManager
from oauth2client.service_account import ServiceAccountCredentials
from config import G_API_FILE, G_API_LINK
from adaptation.isdayoff import AsyncProdCalendar
from adaptation.workdays import add_working_days, parse_date
from loader import db
from utils import queries

CREDENTIALS_PATH = G_API_FILE
SPREADSHEET_URL = G_API_LINK


class GoogleSheetsProcessor:
    """Класс для работы с Google API"""

    def __init__(self, credentials_path : str = CREDENTIALS_PATH):
        """Инициализация с проверкой учетных данных"""
        if not Path(credentials_path).exists():
            raise FileNotFoundError(
                f"Файл учетных данных не найден: {credentials_path}")

        self.credentials_path = credentials_path
        self.client_manager = AsyncioGspreadClientManager(self._authorize)
        self._agc = None
        self._spreadsheet = None
        self._current_url = None

    def _authorize(self):
        """Генератор учетных данных Google API"""
        return ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_path,
            [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'])

    async def _get_client(self):
        """Получение авторизованного клиента (с кешированием)"""
        if not self._agc:
            self._agc = await self.client_manager.authorize()
        return self._agc

    async def _get_spreadsheet(self, spreadsheet_url: str):
        """Получение объекта таблицы (с кешированием)"""
        if not self._spreadsheet or self._current_url != spreadsheet_url:
            agc = await self._get_client()
            self._spreadsheet = await agc.open_by_url(spreadsheet_url)
            self._current_url = spreadsheet_url
        return self._spreadsheet

    async def all_data_to_db(
            self,
            spreadsheet_url: str = SPREADSHEET_URL,
            row_limit: Optional[int] = None) -> dict:
        """
        Перенос данных из Google Sheets в локальную БД
        Args:
            spreadsheet_url: URL таблицы
            row_limit: Ограничение по количеству строк
        """
        if not spreadsheet_url:
            raise ValueError("URL таблицы не может быть пустым")
        try:
            spreadsheet = await self._get_spreadsheet(spreadsheet_url)
            worksheet = await spreadsheet.get_worksheet(0)
            async with AsyncProdCalendar() as calendar:
                if row_limit:
                    all_data = await worksheet.get_values(
                        range_name=f'2:{row_limit}',
                        major_dimension='ROWS')
                else:
                    all_data = (await worksheet.get_all_values())[1:]
                updates = []
                db_data = []
                processed_rows = 0
                skipped_rows = 0
                for row_idx, row_data in enumerate(all_data, start=2):
                    if row_data[18] == '1':
                        skipped_rows += 1
                        continue
                    try:
                        start_date = await parse_date(row_data[5])
                        start_date_add = await add_working_days(
                            start_date,
                            3,
                            calendar)
                        db_data.append((
                            row_data[0], row_data[1], row_data[3],
                            row_data[4], row_data[5], start_date_add))
                        updates.append((row_idx, 19, 1))
                        processed_rows += 1
                    except Exception as e:
                        print(f"Ошибка при обработке строки {row_idx}: {e}")
                        continue
                await db.postmany(queries.GS_2_DB, db_data)
                try:
                    await worksheet.batch_update([{'range': f"R{row}C{col}",
                                                   'values': [[value]]} for row, col, value in updates])
                except AttributeError:
                    for row, col, value in updates:
                        await worksheet.update_cell(row, col, value)
            return {
                'status': 'Успешный успех!',
                'processed': processed_rows,
                'skipped': skipped_rows}
        except Exception as e:
            raise ValueError(f"Ошибка обработки таблицы: {e}")

    async def update_cell_by_name(
            self,
            name: str,
            column: str,
            value: Union[str, int, float],
            spreadsheet_url: str = SPREADSHEET_URL,
            key_column: str = 'A') -> bool:
        """
        Обновление ячейки по значению в ключевом столбце
        """
        try:
            spreadsheet = await self._get_spreadsheet(spreadsheet_url)
            worksheet = await spreadsheet.get_worksheet(0)
            cell = await worksheet.find(
                name.strip(),
                in_column=ord(key_column.upper()) - ord('A') + 1)
            if not cell:
                return False
            update_range = f"{column.upper()}{cell.row}"
            update_data = [[value]]
            await worksheet.update(
                range_name=update_range,
                values=update_data,
                value_input_option='USER_ENTERED')
            return True
        except Exception as e:
            print(f"Ошибка обновления: {str(e)}")
            return False


async def sheets_main():
    """Тестовая функция"""
    try:
        start_time = datetime.now()
        processor = GoogleSheetsProcessor(CREDENTIALS_PATH)
        await processor.all_data_to_db(SPREADSHEET_URL)
        # await processor.update_cell_by_name(
        #     spreadsheet_url=SPREADSHEET_URL,
        #     name="Зайченко Диана Борисовна",  # Значение в столбце A
        #     column="G",  # Столбец для обновления
        #     value="TEST")
        stop_time = datetime.now()
        time_delta = stop_time - start_time
        print(f'Времени затрачено: {time_delta}')

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except ValueError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(sheets_main())
