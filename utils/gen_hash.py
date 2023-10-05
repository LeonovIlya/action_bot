import hashlib
import openpyxl

# НЕЗАБУДЬ ПОМЕНЯТЬ RANGE!!!
# Старт - номер строки экселя с которой начинать
# Конец - номер строки экселя + 1!
# book = openpyxl.load_workbook('pwd.xlsx')
# sheet = book.active
# for i in range(2, 361):
#    sheet[f'D{i}'] = hashlib.sha512(
#        sheet[f'C{i}'].value.encode('utf-8')).hexdigest()
# book.save('pwd.xlsx')


pwd = ''
result = hashlib.sha512(pwd.encode('utf-8')).hexdigest()
print(result)
