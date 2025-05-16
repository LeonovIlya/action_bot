import asyncio
from gspread_asyncio import AsyncioGspreadClientManager, AsyncioGspreadSpreadsheet
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
from datetime import date, timedelta, datetime
from typing import Optional
from config import G_API_FILE, G_API_LINK

from isdayoff import AsyncProdCalendar
from workdays import add_working_days

CREDENTIALS_PATH = G_API_FILE
SPREADSHEET_URL = G_API_LINK

DAYS_DELTA = {1: 6, 7: 7, 14: 8, 21: 9, 42: 10}


async def add_working_days(
        start_date: date,
        days_to_add: int,
        calendar: AsyncProdCalendar,
        callback: Optional[callable] = None) -> date:
    current_date = start_date
    added_days = 0
    while added_days < days_to_add:
        current_date += timedelta(days=1)
        day_type = await calendar.check(current_date)
        if day_type == 0:
            added_days += 1
            if callback:
                await callback(current_date, added_days, days_to_add)
    return current_date


async def parse_date(date_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y")
    except (ValueError, TypeError):
        return None


class GoogleSheetsProcessor:
    def __init__(self, credentials_path: str):
        if not Path(credentials_path).exists():
            raise FileNotFoundError(f"Файл учетных данных не найден: {credentials_path}")
        self.credentials_path = credentials_path
        self.client_manager = AsyncioGspreadClientManager(self._authorize)
        self.spreadsheet: Optional[AsyncioGspreadSpreadsheet] = None

    def _authorize(self):
        return ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_path,
            [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )

    async def process_sheet(self, spreadsheet_url: str) -> dict:
        if not spreadsheet_url:
            raise ValueError("URL таблицы не может быть пустым")
        try:
            agc = await self.client_manager.authorize()
            spreadsheet = await agc.open_by_url(spreadsheet_url)
            worksheet = await spreadsheet.get_worksheet(0)
            row_num = 2
            processed_rows = 0
            skipped_rows = 0
            while True:
                e_cell = await worksheet.cell(row_num, 5)
                if not e_cell.value:
                    break
                r_cell = await worksheet.cell(row_num, 18)
                if r_cell.value == "1":
                    skipped_rows += 1
                    row_num += 1
                    continue
                if not r_cell.value:
                    e_cell = await worksheet.cell(row_num, 5)
                    e_cell_value = await parse_date(e_cell.value)
                    for i, k in DAYS_DELTA.items():
                        async with AsyncProdCalendar() as calendar:
                            result = await add_working_days(e_cell_value, i, calendar)
                            await worksheet.update_cell(row_num, k, result.strftime('%d-%m-%Y'))
                    processed_rows += 1
                row_num += 1
            return {
                'processed_rows': processed_rows,
                'skipped_rows': skipped_rows,
                'last_processed_row': row_num - 1
            }
        except Exception as e:
            raise ValueError(f"Ошибка обработки таблицы: {str(e)}")


async def main():
    try:
        start_time = datetime.now()
        processor = GoogleSheetsProcessor(CREDENTIALS_PATH)
        result = await processor.process_sheet(SPREADSHEET_URL)
        print(f"Обработка завершена. Обработано строк: {result['processed_rows']}")
        print(f"Пропущено строк (R=1): {result['skipped_rows']}")
        print(f"Последняя обработанная строка: {result['last_processed_row']}")
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
    asyncio.run(main())
