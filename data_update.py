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
    pattern = r"AW(\d{4})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
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
            'F10': 'G1',
            'F01D': 'G1/8',
            'F02D': 'G1/4',
            'F03D': 'G3/8',
            'F04D': 'G1/2',
            'F06D': 'G3/4',
            'F10D': 'G1'
        }.get(threads, '')
        data['value7'] = thread
        #Условие для AW4000-06, там расход 4500 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value5'] = str(4500)
    return (num_lines)


def data_update_afxln01(name, data, num_lines):
    #value4 - расход, value6 - резьба
    pattern = r"AF(\d{4})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
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
            'F10': 'G1',
            'F01D': 'G1/8',
            'F02D': 'G1/4',
            'F03D': 'G3/8',
            'F04D': 'G1/2',
            'F06D': 'G3/4',
            'F10D': 'G1'

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
    pattern = r"AC(\d{4})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
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
            'F10': 'G1',
            'F01D': 'G1/8',
            'F02D': 'G1/4',
            'F03D': 'G3/8',
            'F04D': 'G1/2',
            'F06D': 'G3/4',
            'F10D': 'G1'
        }.get(threads, '')
        data['value7'] = thread
    return (num_lines)