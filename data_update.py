import re


# Вспомогательная функция для определения наличия выражения в строке.
# Например, я сопоставляю, есть ли 01, 02, 03 в строках 01, G01, 02S и т.д.
def contains_any_substring(long_string, substrings):
    for substring in substrings:
        if substring in long_string:
            return True
    return False


# типовой шаблон для добавления нового обработчика серий
#def data_update_*****(name, data, num_lines):
#   pattern = r"([A-Z]+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
#   match = re.search(pattern, name)
#   if match:
#       # Извлекаем группы
#       first_part = str(match.group(1))  # Серия фитинга
#       first_digits = str(match.group(2))  # БРС
#       second_group = str(match.group(3))  # БРС/резьба
#
#   return(num_lines)
def data_update_kqxln01(name, data, num_lines):
    #value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"([A-Z]+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        # Сейчас обработаем резьбовые фитинги
        substrings = ['01', '02', '03', '04', 'M3', 'M5', 'M6']
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, substrings)
        if first_part in ['KQH', 'KQS', 'KQF', 'KQL', 'KQW', 'KQK', 'KQV', 'KQT', 'KQY',
                          'KQVF', 'KQU', 'KQLF'] and have_thread:
            num_lines += 1
            if first_digits == '16':
                data['value2'] = str(0.8)
            data['value4'] = str(first_digits).lstrip("0")
            thread = {
                '01': 'R1/8',
                '02': 'R1/4',
                '03': 'R3/8',
                '04': 'R1/2',
                '01S': 'R1/8',
                '02S': 'R1/4',
                '03S': 'R3/8',
                '04S': 'R1/2',
                'G01': 'G1/8',
                'G02': 'G1/4',
                'G03': 'G3/8',
                'G04': 'G1/2',
                'M3': 'M3',
                'M5': 'M5',
                'M6': 'M6',
            }.get(second_group, '')
            if first_part == 'KQLF':  # У KQLF обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС
        if second_group in ['99', '00']:
            if first_digits == '16':
                data['value2'] = str(0.8)
            data['value4'] = str(first_digits).lstrip("0")

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16', '14']:
            num_lines += 1
            if first_digits == '16':
                data['value2'] = str(0.8)
            data['value4'] = str(first_digits).lstrip("0")
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

        # Условие для KQT06-04-XLN01 и подобных, здесь например 04 опознало как резьбу, а это БРС
        if '06-04' in name:
            # num_lines += 1 - здесь не увеличиваем кол-во строк, т.к. в 1 цикле зацепило по 04 и увеличило.
            # Сейчас повторно обрабатываем
            data['value4'] = str(first_digits).lstrip("0")
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")
    # Обработка KQP
    pattern = r"KQP(\d{2})"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))
        data['value4'] = str(first_digits).lstrip("0")
    return (num_lines)


def data_update_awxln01(name, data, num_lines):
    #value5 - расход, value7 - резьба
    pattern = r"AW(\d{4})-(F?\d{2})(?:D)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '550',
            '3000': '2000',
            '4000': '4000',
            '5000': '5000'
        }.get(sizes, '')
        data['value5'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1'
        }.get(threads, '')
        data['value7'] = thread
        #Условие для AW4000-06, там расход 4500 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value5'] = str(4500)
    return (num_lines)


def data_update_afxln01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AF(\d{4})-(F?\d{2})(?:D)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '1000': '110',
            '2000': '750',
            '3000': '1500',
            '4000': '4000',
            '5000': '7000'
        }.get(sizes, '')
        data['value4'] = size
        thread = {
            'M5': 'M5',
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1'
        }.get(threads, '')
        data['value6'] = thread
        #Условие для AF4000-06, там расход 6000 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value4'] = str(6000)
    return (num_lines)


def data_update_arxln01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AR(\d{4})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '1000': '100',
            '2000': '550',
            '3000': '2500',
            '4000': '6000',
            '5000': '8000'
        }.get(sizes, '')
        data['value4'] = size
        thread = {
            'M5': 'M5',
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1'
        }.get(threads, '')
        data['value6'] = thread
        #Условие для AR1000, давление ниже
        if sizes == '1000':
            data['value2'] = str(0.7)
            data['value3'] = str('0.05 ~ 0.7')
    return (num_lines)


def data_update_alxln01(name, data, num_lines):
    #value3 - расход, value5 - резьба
    pattern = r"AL(\d{4})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '800',
            '3000': '1700',
            '4000': '5000',
            '5000': '9000'
        }.get(sizes, '')
        data['value3'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1'
        }.get(threads, '')
        data['value5'] = thread
        #Условие для G3/4
        if sizes == '4000' and thread == 'G3/4':
            data['value3'] = str(6300)
        if sizes == '5000' and thread == 'G3/4':
            data['value3'] = str(7000)
    return (num_lines)


def data_update_vhsxln01(name, data, num_lines):
    #value3 - расход, value4 - расход выхлоп, value6 - резьба, value7 - резьба выхлоп
    pattern = r"VHS(\d{4})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size_exh = {
            '2000': 'G1/8',
            '3000': 'G1/4',
            '4000': 'G3/8',
            '5000': 'G1/2'
        }.get(sizes, '')
        data['value7'] = size_exh
        thread = {
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1'
        }.get(threads, '')
        data['value6'] = thread
        #Условия по расходу
        if sizes == '2000':
            data['value3'] = str(0.7)
            data['value4'] = str(0.8)
        elif sizes == '3000':
            if thread == 'G1/4':
                data['value3'] = str(0.8)
                data['value4'] = str(0.7)
            elif thread == 'G3/8':
                data['value3'] = str(1.7)
                data['value4'] = str(1.6)
        elif sizes == '4000':
            if thread == 'G3/8':
                data['value3'] = str(2)
                data['value4'] = str(2)
            elif thread == 'G1/2':
                data['value3'] = str(3)
                data['value4'] = str(2)
        elif sizes == '5000':
            if thread == 'G3/4':
                data['value3'] = str(4.3)
                data['value4'] = str(2.9)
            elif thread == 'G1':
                data['value3'] = str(6.7)
                data['value4'] = str(2.9)
    return (num_lines)

def data_update_acxln01(name, data, num_lines):
    #value5 - расход, value7 - резьба
    pattern = r"AC(\d{4})-(F?\d{2})(?:D)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '500',
            '3000': '1700',
            '4000': '3000',
            '5000': '4000',
            '2010': '500',
            '3010': '1700',
            '4010': '3000',
            '5010': '4000',
        }.get(sizes, '')
        data['value5'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1'
        }.get(threads, '')
        data['value7'] = thread
    return (num_lines)

def data_update_amgxkv01(name, data, num_lines):
    #value3 - расход, value5 - резьба
    pattern = r"AMG(.+)-(F?\d{2})(?:D)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '150C': '300',
            '250C': '750',
            '350C': '1500',
            '450C': '2200',
            '550C': '3700',
            '650': '6000',
            '850': '12000'
        }.get(sizes, '')
        data['value3'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1',
            'F14': 'G1 1/2',
            'F20': 'G2',
            '01': 'Rc1/8',
            '02': 'Rc1/4',
            '03': 'Rc3/8',
            '04': 'Rc1/2',
            '06': 'Rc3/4',
            '10': 'Rc1',
            '14': 'Rc1 1/2',
            '20': 'Rc2'
        }.get(threads, '')
        data['value5'] = thread
    return (num_lines)

def data_update_affxkv01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AFF(.+)-(F?\d{2})(?:D)?(?:C)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2C': '300',
            '4C': '750',
            '8C': '1500',
            '11C': '2200',
            '22C': '3700',
            '37B': '6000',
            '75B': '12000'
        }.get(sizes, '')
        data['value4'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1',
            'F14': 'G1 1/2',
            'F20': 'G2',
            '01': 'Rc1/8',
            '02': 'Rc1/4',
            '03': 'Rc3/8',
            '04': 'Rc1/2',
            '06': 'Rc3/4',
            '10': 'Rc1',
            '14': 'Rc1 1/2',
            '20': 'Rc2'
        }.get(threads, '')
        data['value6'] = thread
    return (num_lines)

def data_update_amxkv01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AM(.+)-(F?\d{2})(?:D)?(?:C)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '150C': '300',
            '250C': '750',
            '350C': '1500',
            '450C': '2200',
            '550C': '3700',
            '650': '6000',
            '850': '12000'
        }.get(sizes, '')
        data['value4'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1',
            'F14': 'G1 1/2',
            'F20': 'G2',
            '01': 'Rc1/8',
            '02': 'Rc1/4',
            '03': 'Rc3/8',
            '04': 'Rc1/2',
            '06': 'Rc3/4',
            '10': 'Rc1',
            '14': 'Rc1 1/2',
            '20': 'Rc2'
        }.get(threads, '')
        data['value6'] = thread
    return (num_lines)

def data_update_amdxkv01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AMD(.+)-(F?\d{2})(?:D)?(?:C)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '150C': '200',
            '250C': '500',
            '350C': '1000',
            '450C': '2000',
            '550C': '3700',
            '650': '6000',
            '850': '12000'
        }.get(sizes, '')
        data['value4'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1',
            'F14': 'G1 1/2',
            'F20': 'G2',
            '01': 'Rc1/8',
            '02': 'Rc1/4',
            '03': 'Rc3/8',
            '04': 'Rc1/2',
            '06': 'Rc3/4',
            '10': 'Rc1',
            '14': 'Rc1 1/2',
            '20': 'Rc2'
        }.get(threads, '')
        data['value6'] = thread
    return (num_lines)

def data_update_amhxkv01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AMH(.+)-(F?\d{2})(?:D)?(?:C)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '150C': '200',
            '250C': '500',
            '350C': '1000',
            '450C': '2000',
            '550C': '3700',
            '650': '6000',
            '850': '12000'
        }.get(sizes, '')
        data['value4'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1',
            'F14': 'G1 1/2',
            'F20': 'G2',
            '01': 'Rc1/8',
            '02': 'Rc1/4',
            '03': 'Rc3/8',
            '04': 'Rc1/2',
            '06': 'Rc3/4',
            '10': 'Rc1',
            '14': 'Rc1 1/2',
            '20': 'Rc2'
        }.get(threads, '')
        data['value6'] = thread
    return (num_lines)

def data_update_amexkv01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AME(.+)-(F?\d{2})(?:D)?(?:C)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '150C': '200',
            '250C': '500',
            '350C': '1000',
            '450C': '2000',
            '550C': '3700',
            '650': '6000',
            '850': '12000'
        }.get(sizes, '')
        data['value4'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1',
            'F14': 'G1 1/2',
            'F20': 'G2',
            '01': 'Rc1/8',
            '02': 'Rc1/4',
            '03': 'Rc3/8',
            '04': 'Rc1/2',
            '06': 'Rc3/4',
            '10': 'Rc1',
            '14': 'Rc1 1/2',
            '20': 'Rc2'
        }.get(threads, '')
        data['value6'] = thread
    return (num_lines)

def data_update_amfxkv01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AMF(.+)-(F?\d{2})(?:D)?(?:C)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '150C': '200',
            '250C': '500',
            '350C': '1000',
            '450C': '2000',
            '550C': '3700',
            '650': '6000',
            '850': '12000'
        }.get(sizes, '')
        data['value4'] = size
        thread = {
            'F01': 'G1/8',
            'F02': 'G1/4',
            'F03': 'G3/8',
            'F04': 'G1/2',
            'F06': 'G3/4',
            'F10': 'G1',
            'F14': 'G1 1/2',
            'F20': 'G2',
            '01': 'Rc1/8',
            '02': 'Rc1/4',
            '03': 'Rc3/8',
            '04': 'Rc1/2',
            '06': 'Rc3/4',
            '10': 'Rc1',
            '14': 'Rc1 1/2',
            '20': 'Rc2'
        }.get(threads, '')
        data['value6'] = thread
    return (num_lines)

def data_update_sy_20(name, data, num_lines):
    #value2 - диапазон давлений, value3 - расход, value4 - напряжение, value6 - резьба/БРС
    #1 группа - типоразмер, 2 - тип распреда, 3 - напряжение, далее кусок не нужен и после черты уже присоединение
    pattern = r"SY(\d{1})(\d{1})20-(.)(?:.+)-(.+)-(?:.+)"
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        types = str(match.group(2))  # Тип
        voltages = str(match.group(3)) # Напряжение
        threads = str(match.group(4))  # Резьба
        # Тут можно переписать покороче, но я не люблю записи типа have_G = 'F' in threads
        # Проверка на G резьбу
        if 'F' in threads:
            threads = threads.replace('F', '')
            have_G = True
        else:
            have_G = False
        # Проверка на БРС
        if 'C' in threads:
            have_C = True
        else:
            have_C = False
        voltage = {
            '1': '100 VAC',
            '2': '200 VAC',
            '3': '110 VAC',
            '4': '220 VAC',
            '5': '24 VDC',
            '6': '12 VDC',
            'V': '6 VDC',
            'S': '5 VDC',
            'R': '3 VDC'
        }.get(voltages, '')
        data['value4'] = voltage
        thread = {
            'M5': 'M5',
            '01': 'G1/8',
            '02': 'G1/4',
            '03': 'G3/8',
            'C4': '4',
            'C6': '6',
            'C8': '8',
            'C10': '10',
            'C12': '12'
        }.get(threads, '')
        # замена названия если БРС и проверка резьбы, если не G, то переделать на Rc
        if have_C:
            data['line6'] = 'Быстроразъемное присоединение, выход (мм)'
        elif not have_G:
            thread = thread.replace('G', 'Rc')
        data['value6'] = thread
        type = {
            '1': '0.15 ~ 0.7',
            '2': '0.1 ~ 0.7',
            '3': '0.2 ~ 0.7',
            '4': '0.2 ~ 0.7',
            '5': '0.2 ~ 0.7'
        }.get(types, '')
        data['value2'] = type
        # https://static.smc.eu/pdf/SY_EU.pdf - стр. 12 pdf
        patterns_and_Cv = {
            r'SY3120(.+)M5(.+)': '0.16',
            r'SY3220(.+)M5(.+)': '0.16',
            r'SY3320(.+)M5(.+)': '0.13',
            r'SY3420(.+)M5(.+)': '0.13',
            r'SY3520(.+)M5(.+)': '0.15 (0.11)',
            r'SY3120(.+)C4(.+)': '0.18',
            r'SY3220(.+)C4(.+)': '0.18',
            r'SY3320(.+)C4(.+)': '0.15',
            r'SY3420(.+)C4(.+)': '0.16',
            r'SY3520(.+)C4(.+)': '0.21 (0.12)',
            r'SY3120(.+)C6(.+)': '0.19',
            r'SY3220(.+)C6(.+)': '0.19',
            r'SY3320(.+)C6(.+)': '0.24',
            r'SY3420(.+)C6(.+)': '0.16',
            r'SY3520(.+)C6(.+)': '0.21 (0.15)',
            r'SY5120(.+)01(.+)': '0.49',
            r'SY5220(.+)01(.+)': '0.49',
            r'SY5320(.+)01(.+)': '0.45',
            r'SY5420(.+)01(.+)': '0.41',
            r'SY5520(.+)01(.+)': '0.61 (0.28)',
            r'SY5120(.+)C4(.+)': '0.20',
            r'SY5220(.+)C4(.+)': '0.20',
            r'SY5320(.+)C4(.+)': '0.19',
            r'SY5420(.+)C4(.+)': '0.19',
            r'SY5520(.+)C4(.+)': '0.21 (0.18)',
            r'SY5120(.+)C6(.+)': '0.33',
            r'SY5220(.+)C6(.+)': '0.33',
            r'SY5320(.+)C6(.+)': '0.33',
            r'SY5420(.+)C6(.+)': '0.33',
            r'SY5520(.+)C6(.+)': '0.42 (0.23)',
            r'SY5120(.+)C8(.+)': '0.45',
            r'SY5220(.+)C8(.+)': '0.45',
            r'SY5320(.+)C8(.+)': '0.39',
            r'SY5420(.+)C8(.+)': '0.39',
            r'SY5520(.+)C8(.+)': '0.56 (0.44)',
            r'SY7120(.+)02(.+)': '0.93',
            r'SY7220(.+)02(.+)': '0.93',
            r'SY7320(.+)02(.+)': '0.70',
            r'SY7420(.+)02(.+)': '0.65',
            r'SY7520(.+)02(.+)': '0.97 (0.61)',
            r'SY7120(.+)C8(.+)': '0.77',
            r'SY7220(.+)C8(.+)': '0.77',
            r'SY7320(.+)C8(.+)': '0.63',
            r'SY7420(.+)C8(.+)': '0.57',
            r'SY7520(.+)C8(.+)': '0.78 (0.57)',
            r'SY7120(.+)C10(.+)': '0.86',
            r'SY7220(.+)C10(.+)': '0.86',
            r'SY7320(.+)C10(.+)': '0.67',
            r'SY7420(.+)C10(.+)': '0.59',
            r'SY7520(.+)C10(.+)': '0.89 (0.61)',
            r'SY9120(.+)02(.+)': '1.7',
            r'SY9220(.+)02(.+)': '1.7',
            r'SY9320(.+)02(.+)': '1.7',
            r'SY9420(.+)02(.+)': '1.6',
            r'SY9520(.+)02(.+)': '1.8 (0.76)',
            r'SY9120(.+)03(.+)': '1.9',
            r'SY9220(.+)03(.+)': '1.9',
            r'SY9320(.+)03(.+)': '1.9',
            r'SY9420(.+)03(.+)': '1.9',
            r'SY9520(.+)03(.+)': '2.2 (0.82)',
            r'SY9120(.+)C8(.+)': '0.96',
            r'SY9220(.+)C8(.+)': '0.96',
            r'SY9320(.+)C8(.+)': '0.99',
            r'SY9420(.+)C8(.+)': '0.99',
            r'SY9520(.+)C8(.+)': '1.0 (0.71)',
            r'SY9120(.+)C10(.+)': '1.4',
            r'SY9220(.+)C10(.+)': '1.4',
            r'SY9320(.+)C10(.+)': '1.4',
            r'SY9420(.+)C10(.+)': '1.3',
            r'SY9520(.+)C10(.+)': '1.5 (0.72)',
            r'SY9120(.+)C12(.+)': '1.6',
            r'SY9220(.+)C12(.+)': '1.6',
            r'SY9320(.+)C12(.+)': '1.6',
            r'SY9420(.+)C12(.+)': '1.4',
            r'SY9520(.+)C12(.+)': '1.7 (0.74)'
        }
        for pattern, flow in patterns_and_Cv.items():
            if re.match(pattern, name):
                data['value3'] = flow
                break
    return (num_lines)


def data_update_kqg2xrt01(name, data, num_lines):
    #value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQG2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        # Сейчас обработаем резьбовые фитинги
        substrings = ['01', '02', '03', '04', 'M5']
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, substrings)
        if first_part in ['H', 'L', 'T', 'F'] and have_thread:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            thread = {
                '01': 'R1/8',
                '02': 'R1/4',
                '03': 'R3/8',
                '04': 'R1/2',
                'M5': 'M5'
            }.get(second_group, '')
            if first_part == 'F':  # У KQG2F обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС
        if second_group in ['00']:
            data['value4'] = str(first_digits).lstrip("0")

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16']:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

    return (num_lines)


def data_update_kqg2xln01(name, data, num_lines):
    #value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQG2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        # Сейчас обработаем резьбовые фитинги
        substrings = ['01', '02', '03', '04', 'M5']
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, substrings)
        if first_part in ['H', 'L', 'T', 'F'] and have_thread:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            thread = {
                '01': 'R1/8',
                '02': 'R1/4',
                '03': 'R3/8',
                '04': 'R1/2',
                'M5': 'M5'
            }.get(second_group, '')
            if first_part == 'F':  # У KQG2F обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС
        if second_group in ['00']:
            data['value4'] = str(first_digits).lstrip("0")

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16']:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

    return (num_lines)


def data_update_kqg2xkv01(name, data, num_lines):
    #value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQG2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        if first_part in ['TF']:
            data['Name_product'] = str(data['Name_product']).replace('Фитинг', 'Коллектор')
        # Сейчас обработаем резьбовые фитинги
        substrings = ['01', '02', '03', '04', 'M5']
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, substrings)
        if first_part in ['H', 'L', 'T', 'F', 'S'] and have_thread:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            thread = {
                '01': 'R1/8',
                '02': 'R1/4',
                '03': 'R3/8',
                '04': 'R1/2',
                'G01': 'G1/8',
                'G02': 'G1/4',
                'G03': 'G3/8',
                'G04': 'G1/2',
                'M5': 'M5'
            }.get(second_group, '')
            data['value5'] = thread

        # Условия для фитингов БРС
        if second_group in ['00']:
            data['value4'] = str(first_digits).lstrip("0")

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16']:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

        # Обработка KQP
    pattern = r"KQG2P-(\d{2})-XKV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))
        data['value4'] = str(first_digits).lstrip("0")

    return (num_lines)


def data_update_kfgxnc01(name, data, num_lines):
    #value4/value5 - место для БРС, value6 - место для резьбы (если есть)
    pattern = r"KFG(?:.+)(\d{2})(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС1
        second_digits = str(match.group(2))  # БРС2
        second_group = str(match.group(3))  # БРС/резьба
        # Сейчас обработаем резьбовые фитинги
        substrings = ['01', '02', '03', '04', 'M5']
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, substrings)
        if have_thread:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            data['value5'] = str(second_digits).lstrip("0")
            thread = {
                '01': 'R1/8',
                '02': 'R1/4',
                '03': 'R3/8',
                '04': 'R1/2',
                'M5': 'M5'
            }.get(second_group, '')
            data['value6'] = thread

        # Условия для фитингов БРС
        if second_group in ['00']:
            data['value4'] = str(first_digits).lstrip("0")
            data['value5'] = str(second_digits).lstrip("0")

        if data['value5'] == '65':
            data['value5'] = '6.5'

    return (num_lines)


def data_update_kfgxrt01(name, data, num_lines):
    #value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KFG(?:.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС1
        second_group = str(match.group(2))  # БРС/резьба
        # Сейчас обработаем резьбовые фитинги
        substrings = ['01', '02', '03', '04', 'M5']
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, substrings)
        if have_thread:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            thread = {
                '01': 'R1/8',
                '02': 'R1/4',
                '03': 'R3/8',
                '04': 'R1/2',
                'M5': 'M5'
            }.get(second_group, '')
            data['value5'] = thread

        # Условия для фитингов БРС
        if second_group in ['00']:
            data['value4'] = str(first_digits).lstrip("0")

    return (num_lines)


def data_update_kfgxnt01(name, data, num_lines):
    #value4/value5 - место для БРС, value6 - место для резьбы (если есть)
    pattern = r"KFG(?:.+)(\d{2})(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС1
        second_digits = str(match.group(2))  # БРС2
        second_group = str(match.group(3))  # БРС/резьба
        # Сейчас обработаем резьбовые фитинги
        substrings = ['01', '02', '03', '04', 'M5']
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, substrings)
        if have_thread:
            num_lines += 1
            data['value4'] = str(first_digits).lstrip("0")
            data['value5'] = str(second_digits).lstrip("0")
            thread = {
                '01': 'R1/8',
                '02': 'R1/4',
                '03': 'R3/8',
                '04': 'R1/2',
                'F01': 'G1/8',
                'F02': 'G1/4',
                'F03': 'G3/8',
                'F04': 'G1/2',
                'M5': 'M5'
            }.get(second_group, '')
            data['value6'] = thread

        # Условия для фитингов БРС
        if second_group in ['00']:
            data['value4'] = str(first_digits).lstrip("0")
            data['value5'] = str(second_digits).lstrip("0")

        if data['value5'] == '25':
            data['value5'] = '2.5'
        elif data['value5'] == '75':
            data['value5'] = '7.5'

    return (num_lines)