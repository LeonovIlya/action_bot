import asyncio
from gspread_asyncio import AsyncioGspreadClientManager, AsyncioGspreadSpreadsheet
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import G_API_FILE, G_API_LINK

from isdayoff import AsyncProdCalendar
from loader import db
from workdays import add_working_days, parse_date
from utils import queries

CREDENTIALS_PATH = G_API_FILE
SPREADSHEET_URL = G_API_LINK

DAYS_TUPLE = (1, 7, 14, 21, 42)


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

    async def all_data_to_db(self, spreadsheet_url: str, row_limit: Optional[int] = None) -> dict:
        if not spreadsheet_url:
            raise ValueError("URL таблицы не может быть пустым")
        try:
            agc = await self.client_manager.authorize()
            spreadsheet = await agc.open_by_url(spreadsheet_url)
            worksheet = await spreadsheet.get_worksheet(0)

            async with AsyncProdCalendar() as calendar:
                if row_limit:
                    all_data = await worksheet.get_values(range_name=f'2:{row_limit}', major_dimension='ROWS')

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
                        days_to_add = []
                        for i in DAYS_TUPLE:
                            day_to_add = await add_working_days(start_date, i, calendar)
                            days_to_add.append(day_to_add)

                        db_data.append((
                            row_data[0], row_data[1], row_data[3], row_data[4], row_data[5], *days_to_add))
                        updates.append((row_idx, 19, 1))
                        processed_rows += 1

                    except Exception as e:
                        print(f"Ошибка при обработке строки {row_idx}: {e}")
                        continue

                await db.postmany(queries.GS_2_DB, db_data)

                try:
                    await worksheet.batch_update([{
                        'range': f"R{row}C{col}",
                        'values': [[value]]
                    } for row, col, value in updates])
                except AttributeError:
                    for row, col, value in updates:
                        await worksheet.update_cell(row, col, value)

            return {
                'status': 'Успешный успех!',
                'processed': processed_rows,
                'skipped': skipped_rows}

        except Exception as e:
            raise ValueError(f"Ошибка обработки таблицы: {str(e)}")


async def main():
    try:
        start_time = datetime.now()
        processor = GoogleSheetsProcessor(CREDENTIALS_PATH)
        result = await processor.all_data_to_db(SPREADSHEET_URL)
        stop_time = datetime.now()
        time_delta = stop_time - start_time
        print(f'Времени затрачено: {time_delta}')
        print(result)

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
    except ValueError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
