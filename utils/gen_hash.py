import hashlib
import openpyxl

# НЕЗАБУДЬ ПОМЕНЯТЬ RANGE!!!
# Старт - номер строки с которой начинать
# Конец - номер строки + 1!
book = openpyxl.load_workbook('users.xlsx')
sheet = book.active
for i in range(2, 192):
    sheet[f'E{i}'] = hashlib.sha512(
        sheet[f'd{i}'].value.encode('utf-8')).hexdigest()
book.save('users.xlsx')
