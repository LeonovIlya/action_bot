import asyncio
import aiosqlite
from gspread_asyncio import AsyncioGspreadClientManager, AsyncioGspreadSpreadsheet
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
from datetime import date, timedelta, datetime
from typing import Optional

from config import G_API_FILE, G_API_LINK

from isdayoff import AsyncProdCalendar
from workdays import add_working_days, parse_date


CREDENTIALS_PATH = G_API_FILE
SPREADSHEET_URL = G_API_LINK

DB_FILE = '../data.db'

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

    async def all_data_to_db(self, spreadsheet_url: str) -> dict:
        if not spreadsheet_url:
            raise ValueError("URL таблицы не может быть пустым")
        # try:
        agc = await self.client_manager.authorize()
        spreadsheet = await agc.open_by_url(spreadsheet_url)
        worksheet = await spreadsheet.get_worksheet(0)
        db_conn = await aiosqlite.connect(DB_FILE)
        all_data = await worksheet.get_all_values()

        for i in all_data[1:]:
            start_date = await parse_date(i[5])
            days_to_add = []
            for k in DAYS_TUPLE:
                day_to_add = await add_working_days(start_date, k,
                                         AsyncProdCalendar())
                days_to_add.append(day_to_add)
            await db_conn.execute('''INSERT INTO adaptation (
                intern_name, intern_email, mentor_name, mentor_ter_num,
                date_start, date_1day, date_1week, date_2week, 
                date_3week, date_6week) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                  (i[0], i[1], i[3], i[4], i[5], *days_to_add))
            await db_conn.commit()
        await db_conn.close()




            # row_num = 2
            # processed_rows = 0
            # skipped_rows = 0
            # while True:
            #     cell_a_data = await worksheet.cell(row_num, 1)
            #     if not cell_a_data.value:
            #         break
            #
            #     cell_s_data = await worksheet.cell(row_num, 19)
            #     if cell_s_data.value == "1":
            #         skipped_rows += 1
            #         row_num += 1
            #         continue
            #
            #     if not cell_s_data.value:
            #         row_data = await worksheet.row_values(row_num)
            #         await db_conn.execute('''INSERT INTO adaptation (
            #         intern_name, intern_email, mentor_name, mentor_ter_num,
            #         date_start) VALUES (?, ?, ?, ?, ?)''', (row_data[0],
            #                                                 row_data[1],
            #                                                 row_data[3],
            #                                                 row_data[4],
            #                                                 row_data[5]))
            #         await db_conn.commit()
            #         await worksheet.update_cell(row_num, 19, '1')
            #         processed_rows += 1
            # return {
            #     'processed_rows': processed_rows,
            #     'skipped_rows': skipped_rows,
            #     'last_processed_row': row_num - 1}
        # except Exception as e:
        #     raise ValueError(f"Ошибка обработки таблицы: {str(e)}")


async def main():
    # try:
    start_time = datetime.now()
    processor = GoogleSheetsProcessor(CREDENTIALS_PATH)
    await processor.all_data_to_db(SPREADSHEET_URL)
    # print(f"Обработка завершена. Обработано строк: {result['processed_rows']}")
    # print(f"Пропущено строк (R=1): {result['skipped_rows']}")
    # print(f"Последняя обработанная строка: {result['last_processed_row']}")
    stop_time = datetime.now()
    time_delta = stop_time - start_time
    print(f'Времени затрачено: {time_delta}')

    # except FileNotFoundError as e:
    #     print(f"Ошибка: {e}")
    # except ValueError as e:
    #     print(f"Ошибка: {e}")
    # except Exception as e:
    #     print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())
