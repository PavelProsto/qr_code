#All hail Pascal!

import base64
import qrcode
import re
import os.path


prefixes_android = {'serial_add': 'cryptopro://csp/license/add/', 'serv_add': 'cryptopro://csp/profile/add/',
                     'root_add': 'cryptopro://csp/root/add/', 'ca_add': 'cryptopro://csp/intermediate/add/',
                     'crl_add': 'cryptopro://csp/crl/add/', 'pfx_add': 'cryptopro://csp/pfx/add/'} 
len_max = 2500 #максимальная длинна на один qr код


def get_from_file(filepath, code_type):
    with open(filepath, 'rb') as binary_data_file:
        if code_type == '0':
            content = base64.b32encode(binary_data_file.read()).decode()
        else:
            content = base64.b64encode(binary_data_file.read()).decode()
    return content


def serial_get():
    while True:
        input_data = input("Введите серийный номер: ")
        if not re.fullmatch(r"^[a-zA-Z0-9]{5}-([a-zA-Z0-9]{5}-){3}[a-zA-Z0-9]{5}$", str(input_data)):
            print('Введённый серийный номер не соответствует формату')
            print('Должен быть вида ххххх-ххххх-ххххх-ххххх-ххххх')
        else:
            break
    return input_data


def file_get():
    while True:
        filepath = input('Введите путь к файлу сертификата \ pfx \ CRL: ')
        if not os.path.isfile(filepath):
            print('Указанный файл не существует или не доступен')
        else:
            break
    return filepath


def prfx_get():
    prfx = None 
    while not prfx:
        cert_type = input('Введите тип файла: Ca, Root, pfx, CRL: ')
        match cert_type:
            case 'CA' | 'ca' | 'Ca': 
                prfx = prefixes_android['ca_add']
            case 'root' | 'Root' | 'ROOT':
                prfx = prefixes_android['root_add']
            case 'PFX' | 'Pfx' | 'pfx': 
                prfx = prefixes_android['pfx_add']
            case 'CRL' | 'Crl' | 'crl': 
                prfx = prefixes_android['crl_add'] 
            case _:
                print('Указан не корректный тип файла!')           
    return cert_type, prfx


def code_type_get():
    while True:
        code_type = str(input('Введите тип кодировки: 2 для base32, 0 для base64: '))
        if code_type in '0, 2':
            break
        else:
            print('Указан не корректный тип кодировки!')
    return code_type



def gen_qr(chunk,cert_type,part_number):
    img = qrcode.make(chunk)
    img.save(cert_type + str(part_number) + '.png')


def serial_gen(serial_nmbr):
    fnl_string = prefixes_android['serial_add'] + serial_nmbr
    gen_qr(fnl_string,'serial', '1')


def cert_gen(filepath, code_type, cert_type, prfx):
    cert_encoded = get_from_file(filepath, code_type)
    if len(cert_encoded) > len_max:
        parts_total = len(cert_encoded) // len_max + 1
        chunks = [cert_encoded[i:i+len_max] for i in range(0, len(cert_encoded), len_max)]
        #for n in range(1, parts_total + 1): #значение n определяет нумерацию сегментов, начнётся она с 1
        #    gen_qr(prfx + str(code_type) + '/' + str(parts_total) + '/' + str(n) + '/' + chunks[n-1], cert_type, n)
        for n in range(parts_total): #значение n определяет нумерацию сегментов, или с 0
            gen_qr(prfx + str(code_type) + '/' + str(parts_total) + '/' + str(n) + '/' + chunks[n], cert_type, n)
    else:
        gen_qr(prfx + code_type + '/1/1/' + cert_encoded, cert_type, '1')



def start_menu():
    print("""Привет! Выбери один из следующих пунктов:
1. QR код для серийного номера
2. QR код для добавления VPN сервера
3. QR код для добавления сертификата или PFX
""")
    usrch = input()
    match usrch:
        case '1':
            serial = serial_get()
            serial_gen(serial.upper())
        case '2':
            auth_type = input('Введите тип аутентификации 1 - сертификат, 2 - логин\пароль, 3 - смешанный: ')
            server_uri = input('Введите URI сервера: ')
            profile_name = input('Введите имя профиля: ')
            gen_qr(prefixes_android['serv_add'] + profile_name + '/' + auth_type + '/' + server_uri + '/', 'uri', '1')
        case '3':
            filepath = file_get()
            cert_type, prfx = prfx_get()
            code_type = code_type_get() 
            cert_gen(filepath, code_type, cert_type, prfx)
        case _:
                print('Указан не корректный пункт меню!')   


if __name__ == "__main__":
    start_menu()
