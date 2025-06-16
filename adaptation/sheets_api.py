"""Модуль для работы с Google API"""

import logging
from pathlib import Path
from typing import Optional, Union, Dict, List, Tuple
from gspread_asyncio import AsyncioGspreadClientManager,\
    AsyncioGspreadSpreadsheet, AsyncioGspreadWorksheet
from oauth2client.service_account import ServiceAccountCredentials

from adaptation.isdayoff import AsyncProdCalendar
from adaptation.workdays import add_working_days, parse_date

from config import G_API_FILE, G_API_LINK
from loader import db
from utils import queries

CREDENTIALS_PATH = G_API_FILE
SPREADSHEET_URL = G_API_LINK

logger = logging.getLogger("bot")


class GoogleSheetsProcessor:
    """Класс для работы с Google Sheets API: чтение, запись, синхронизация с
    БД. """

    def __init__(self, credentials_path: str = CREDENTIALS_PATH):
        """Инициализация клиента Google Sheets."""
        if not Path(credentials_path).exists():
            logger.error(f"Файл учетных данных не найден: {credentials_path}")
            raise FileNotFoundError(
                f"Файл учетных данных не найден: {credentials_path}")
        self.credentials_path = credentials_path
        self.client_manager = AsyncioGspreadClientManager(self._authorize)
        self._agc = None
        self._spreadsheet: Optional[AsyncioGspreadSpreadsheet] = None
        self._current_url = None

    def _authorize(self):
        """Создает учетные данные для авторизации в Google API."""
        logger.debug("Авторизация в Google API")
        return ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_path,
            [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'])

    async def _get_client(self):
        """Получает или создает клиент Google Sheets (кешировано)."""
        if not self._agc:
            self._agc = await self.client_manager.authorize()
            logger.debug("Создан новый клиент Google Sheets")
        return self._agc

    async def _get_spreadsheet(self, spreadsheet_url: str)\
            -> AsyncioGspreadSpreadsheet:
        """Получает объект таблицы по URL (кешировано)."""
        if not self._spreadsheet or self._current_url != spreadsheet_url:
            agc = await self._get_client()
            self._spreadsheet = await agc.open_by_url(spreadsheet_url)
            self._current_url = spreadsheet_url
            logger.info(f"Открыта таблица: {spreadsheet_url}")
        return self._spreadsheet

    async def _get_worksheet(self, spreadsheet_url: str)\
            -> AsyncioGspreadWorksheet:
        """Возвращает первый лист таблицы."""
        spreadsheet = await self._get_spreadsheet(spreadsheet_url)
        worksheet = await spreadsheet.get_worksheet(0)
        logger.debug(f"Получен лист таблицы: {spreadsheet_url}")
        return worksheet

    async def all_data_to_db(
            self,
            spreadsheet_url: str = SPREADSHEET_URL,
            row_limit: Optional[int] = None) -> Dict[str, Union[str, int]]:
        """Переносит данные из Google Sheets в локальную БД."""
        if not spreadsheet_url:
            logger.warning("URL таблицы не может быть пустым")
            raise ValueError("URL таблицы не может быть пустым")
        try:
            worksheet = await self._get_worksheet(spreadsheet_url)
            async with AsyncProdCalendar() as calendar:
                if row_limit:
                    all_data = await worksheet.get_values(
                        range_name=f'2:{row_limit}', major_dimension='ROWS')
                else:
                    all_data = (await worksheet.get_all_values())[1:]
                logger.info(f"Загружено {len(all_data)} строк для обработки")
                db_records: List[Tuple] = []
                updates: List[Dict] = []
                processed_rows = 0
                skipped_rows = 0
                for row_idx, row in enumerate(all_data, start=2):
                    if row[18] == '1':
                        skipped_rows += 1
                        continue
                    try:
                        start_date = await parse_date(row[5])
                        start_date_add = await add_working_days(
                            start_date, 3, calendar)
                        db_records.append((
                            row[0], row[1], row[3], row[4], row[5],
                            start_date_add))
                        updates.append({'range': f"S{row_idx}",
                                        'values': [[1]]})
                        processed_rows += 1
                    except Exception as e:
                        logger.error(
                            f"Ошибка при обработке строки {row_idx}: {e}",
                            exc_info=True)
                        continue
                if db_records:
                    await db.postmany(queries.GS_2_DB, db_records)
                    logger.info(f"Записано в БД: {len(db_records)} записей")
                if updates:
                    try:
                        await worksheet.batch_update(updates)
                        logger.info(
                            f"Обновлено ячеек в Google Sheets: {len(updates)}")
                    except AttributeError:
                        logger.warning("batch_update не поддерживается, "
                                       "использую update_cell по одному")
                        for update in updates:
                            col_letter = update["range"][0]
                            col_index = ord(col_letter.upper()) - ord('A') + 1
                            row_number = int(update["range"][1:])
                            value = update["values"][0][0]
                            await worksheet.update_cell(
                                row_number, col_index, value)
                            logger.debug(
                                f"Обновлена ячейка {update['range']} "
                                f"значением {value}")
                return {'status': 'Успешный успех!',
                        'processed': processed_rows,
                        'skipped': skipped_rows}
        except Exception as e:
            logger.error(f"Ошибка обработки таблицы: {e}", exc_info=True)
            raise RuntimeError(f"Ошибка обработки таблицы: {e}")

    async def update_cells_by_name(
            self,
            name: str,
            cell_data: Dict[str, Union[str, int, float]],
            key_column: str = 'A',
            spreadsheet_url: str = SPREADSHEET_URL) -> bool:
        """Обновляет несколько ячеек в строке, где в столбце `key_column`
        находится значение `name`. """
        try:
            worksheet = await self._get_worksheet(spreadsheet_url)
            logger.debug(f"Поиск строки с ключом '{name}' в столбце "
                         f"{key_column}")
            cell = await worksheet.find(
                name.strip(),
                in_column=ord(key_column.upper()) - ord('A') + 1)
            if not cell:
                logger.warning(f"Строка с ключом '{name}' не найдена")
                return False
            data = [{'range': f"{col.upper()}{cell.row}", 'values': [[val]]}
                    for col, val in cell_data.items()]
            logger.info(
                f"Обновление ячеек в строке "
                f"{cell.row}: {list(cell_data.keys())}")
            await worksheet.batch_update(data,
                                         value_input_option='USER_ENTERED')
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления: {str(e)}", exc_info=True)
            return False
