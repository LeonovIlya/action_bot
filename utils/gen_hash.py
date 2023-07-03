import hashlib
import openpyxl

book = openpyxl.load_workbook('users.xlsx')
sheet = book.active
for i in range(3, 828):
    sheet[f'E{i}'] = hashlib.sha512(sheet[f'd{i}'].value.encode('utf-8')).hexdigest()
book.save('users.xlsx')
