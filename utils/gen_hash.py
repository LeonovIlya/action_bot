import hashlib
import openpyxl
import secrets
import string


def generate_password():
    letters = [
        secrets.choice(string.ascii_uppercase),
        *[secrets.choice(string.ascii_lowercase) for _ in range(2)],
        secrets.choice(string.ascii_uppercase)]
    digits = [secrets.choice(string.digits) for _ in range(4)]
    return ''.join(letters) + ''.join(digits)
#
#
# # НЕЗАБУДЬ ПОМЕНЯТЬ RANGE!!!
# # Старт - номер строки экселя с которой начинать
# # Конец - номер строки экселя + 1!
# # book = openpyxl.load_workbook('pwd_mwc.xlsx')
# book = openpyxl.load_workbook('pwd.xlsx')
# sheet = book['Center']
# for i in range(310, 318):
#     sheet[f'C{i}'] = generate_password()
#     sheet[f'D{i}'] = hashlib.sha512(
#         sheet[f'C{i}'].value.encode('utf-8')).hexdigest()
# book.save('pwd_mwc.xlsx')


pwd = generate_password()
pwd_hash = hashlib.sha512(pwd.encode('utf-8')).hexdigest()
print(pwd)
print('----------------------------------------------------------------')
print(pwd_hash)
