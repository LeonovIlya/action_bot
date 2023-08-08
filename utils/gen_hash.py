import hashlib
import openpyxl

# НЕЗАБУДЬ ПОМЕНЯТЬ RANGE!!!
# Старт - номер строки экселя с которой начинать
# Конец - номер строки экселя + 1!
book = openpyxl.load_workbook('users.xlsx')
sheet = book.active
for i in range(2, 212):
    sheet[f'E{i}'] = hashlib.sha512(
        sheet[f'd{i}'].value.encode('utf-8')).hexdigest()
book.save('users.xlsx')
