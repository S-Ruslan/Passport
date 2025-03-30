import re


# Вспомогательная функция для определения наличия выражения в строке.
# Например, я сопоставляю, есть ли 01, 02, 03 в строках 01, G01, 02S и т.д.
def contains_any_substring(long_string, substrings):
    for substring in substrings:
        if substring in long_string:
            return True
    return False


# Табличка для идентификации наличия мелкой резьбы у фитингов
little_thread = ['01', '02', '03', '04', 'M3', 'M5', 'M6', 'M7']
# Табличка для идентификации наличия любой стандартной резьбы
all_thread = ['01', '02', '03', '04', '06', '10', '12', '14', '20', 'M3', 'M5', 'M6', 'M7']
# Перевод резьбы в нормальный вид паспорта
# не более 1/2 для фитингов
thread_fittings = {
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
                'F01': 'G1/8',
                'F02': 'G1/4',
                'F03': 'G3/8',
                'F04': 'G1/2',
                'M3': 'M3',
                'M5': 'M5',
                'M6': 'M6',
                'M7': 'M7'
            }
# Перевод резьбы в нормальный вид паспорта
# Варианты для общей базы, где нет брс
thread_not_fittings = {
                'M5': 'M5',
                'M5A': 'M5',
                'F01': 'G1/8',
                'F02': 'G1/4',
                'F03': 'G3/8',
                'F04': 'G1/2',
                'F06': 'G3/4',
                'F10': 'G1',
                'F14': 'G1 1/2',
                'F20': 'G2',
                'N01': 'NPT1/8',
                'N02': 'NPT1/4',
                'N03': 'NPT3/8',
                'N04': 'NPT1/2',
                'N06': 'NPT3/4',
                'N10': 'NPT1',
                '01': 'Rc1/8',
                '02': 'Rc1/4',
                '03': 'Rc3/8',
                '04': 'Rc1/2',
                '06': 'Rc3/4',
                '10': 'Rc1',
                '14': 'Rc1 1/2',
                '20': 'Rc2'
            }


def data_update_kqxln01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"([A-Z]+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        # Поправка на давление для 16 диаметра и сразу занесение значения БРС
        if first_digits == '16':
            data['value2'] = '0.8'
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            if first_part == 'KQLF':  # У KQLF обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС с разными выходами
        # data['line5'] = data['line4'] - это переобозначение строки резьбовое соединение на быстроразъемное
        if second_group in ['06', '08', '10', '12', '16', '14']:
            num_lines += 1
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

        # Условие для KQT06-04-XLN01 и подобных, здесь например 04 опознало как резьбу, а это БРС
        if '06-04' in name:
            # num_lines += 1 - здесь не увеличиваем кол-во строк, т.к. в 1 цикле зацепило по 04 и увеличило.
            # Сейчас повторно обрабатываем
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

    # Обработка KQP
    pattern = r"KQP(\d{2})"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))
        data['value4'] = str(first_digits).lstrip("0")
    return num_lines


def data_update_awxln01(name, data, num_lines):
    # value5 - расход, value7 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value7'] = thread
        # Условие для AW4000-06, там расход 4500 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value5'] = '4500'
    return num_lines


def data_update_awxrt01(name, data, num_lines):
    # value5 - расход, value7 - резьба
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
            '5000': '5500'
        }.get(sizes, '')
        data['value5'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value7'] = thread
        # Условие для AW4000-06, там расход 4500 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value5'] = '4500'
    return num_lines


def data_update_awx425xnt01(name, data, num_lines):
    # value5 - расход, value7 - резьба
    pattern = r"AW(\d{4})-(F?\d{2})(?:B)?(?:G)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '550',
            '3000': '2000',
            '4000': '4000',
            '5000': '5500'
        }.get(sizes, '')
        data['value5'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value7'] = thread
        # Условие для AW4000-06, там расход 4500 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value5'] = '4500'
    return num_lines


def data_update_afxln01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
        # Условие для AF4000-06, там расход 6000 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value4'] = '6000'
    return num_lines


def data_update_afxrt01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
        # Условие для AF4000-06, там расход 6000 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value4'] = '6000'
    return num_lines


def data_update_afx425xnt01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"AF(\d{4})-(F?\d{2})(?:B)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '750',
            '3000': '1500',
            '4000': '4000',
            '5000': '7000'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
        # Условие для AF4000-06, там расход 6000 вместо 4000
        if size == '4000' and thread == 'G3/4':
            data['value4'] = '6000'
    return num_lines


def data_update_afhxln01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"AFH(\d{4})-(F?\d{2})-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '37',
            '4000': '50',
            '6000': '153'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        # Артикулы сформированы как будто Rc резьба, но по факту G
        thread = thread.replace('Rc', 'G')
        data['value6'] = thread
    return num_lines


def data_update_afhxnt01(name, data, num_lines):
    # value5 - резьба
    pattern = r"AFH(\d{4})-(F?\d{2})-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        # РАСХОДА НЕТ!!! Оставил кусок кода на будущее, как измерят. Пока только резьба
        size = {
            '2000': '....',
            '4000': '....',
            '6000': '....'
        }.get(sizes, '')
        # data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value5'] = thread
    return num_lines


def data_update_aw20lxlc01(name, data, num_lines):
    # value6 - резьба
    pattern = r"AW20-(.{3})BG-2-L-XLC01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        threads = str(match.group(1))  # Резьба
        thread = {
            'F02': 'G1/4',
            'N02': 'NPT1/4'
        }.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_awsxsp01(name, data, num_lines):
    # value5 - расход, value7 - резьба
    pattern = r"AW(\d{3})S-(F?N?\d{2})(?:D)?(-L)?-XSP01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        temp = str(match.group(3))  # Проверка исполнения L
        size = {
            '200': '1850',
            '400': '2200',
            '600': '7600'
        }.get(sizes, '')
        data['value5'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value7'] = thread
        # Поиск L
        if temp == '-L':
            data['value6'] = '-40 ~ +50'
        # Условие для других резьб
        if sizes == '400' and thread in ['G1/2', 'NPT1/2']:
            data['value5'] = '2500'
        if sizes == '600' and thread in ['G1', 'NPT1']:
            data['value5'] = '8000'
    return num_lines


def data_update_awhxln01(name, data, num_lines):
    # value5 - расход, value7 - резьба
    pattern = r"AWH(\d{4})-(F?\d{2})-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '25',
            '4000': '35',
            '6000': '70'
        }.get(sizes, '')
        data['value5'] = size
        thread = thread_not_fittings.get(threads, '')
        # Артикулы сформированы как будто Rc резьба, но по факту G
        thread = thread.replace('Rc', 'G')
        data['value7'] = thread
    return num_lines


def data_update_ip300(name, data, num_lines):
    # value5 - расход, value6 - температура, value7 - резьба, value8 - материал корпуса
    pattern = r"IP3(.)(.)(.)(.)(?:.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        materials = str(match.group(2))  # Материал корпуса
        threads = str(match.group(3))  # Тип резьбы
        temps = str(match.group(4))  # Температура
        size = {
            '0': '240',
            '1': '1900'
        }.get(sizes, '')
        data['value5'] = size
        type_thread = {
            'N': 'NPT',
            'G': 'G',
            'P': 'Rc'
        }.get(threads, '')
        thread = {
            '0': '1/4',
            '1': '1/2'
        }.get(sizes, '')
        data['value7'] = type_thread + thread
        mat = {
            '0': 'Алюминиевый сплав',
            '5': 'Нерж. сталь 316'
        }.get(materials, '')
        data['value8'] = mat
        temp = {
            'S': '-20 ~ +70',
            'H': '-20 ~ +120',
            'L': '-40 ~ +70',
            'U': '-60 ~ +70'
        }.get(temps, '')
        data['value6'] = temp
    return num_lines


def data_update_afmxkv01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"AFM(\d{2})-(F?\d{2})(?:D)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '20': '200',
            '30': '450',
            '40': '1100'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_afdxkv01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"AFD(\d{2})-(F?\d{2})(?:D)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '20': '120',
            '30': '240',
            '40': '600'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_arxln01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
        # Условие для AR1000, давление ниже
        if sizes == '1000':
            data['value2'] = '0.7'
            data['value3'] = '0.05 ~ 0.7'
    return num_lines


def data_update_arxrt01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"AR(\d{4})(?:K)?-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '1000': '100',
            '2000': '550',
            '2500': '2000',
            '3000': '2500',
            '4000': '6000',
            '5000': '8000'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
        # Условие для AR1000, давление ниже
        if sizes == '1000':
            data['value2'] = '0.7'
            data['value3'] = '0.05 ~ 0.7'
    return num_lines


def data_update_arx425xnt01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"AR(\d{4})-(F?\d{2})(?:B)?(?:G)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '550',
            '3000': '2500',
            '4000': '6000',
            '5000': '8000'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_ap100xbr01(name, data, num_lines):
    # value6 - резьба
    pattern = r"AP100-(\d{2})B-XBR01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        threads = str(match.group(1))  # Резьба
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_ar_25xln01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"AR(\d{1})25-(F?\d{2})-XLN01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '8': '16000',
            '9': '18000'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_arhxln01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"ARH(\d{4})-(F?\d{2})-XLN01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '25',
            '4000': '35',
            '6000': '100'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        # Артикулы сформированы как будто Rc резьба, но по факту G
        thread = thread.replace('Rc', 'G')
        data['value6'] = thread
    return num_lines


def data_update_arhxmp01(name, data, num_lines):
    # value4 - расход, value6 - резьба
    pattern = r"ARH(\d{4})-(F?\d{2})-XMP01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '6000': '100',
            '8000': '-'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_irxln01(name, data, num_lines):
    # value3 - диапазон давления, value4 - расход, value6 - резьба
    pattern = r"IR(\d{4})-(F?\d{2})-XLN01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        pressure = {
            '1000': '0.005 ~ 0.2',
            '1010': '0.01 ~ 0.4',
            '1020': '0.01 ~ 0.8',
            '2000': '0.005 ~ 0.2',
            '2010': '0.01 ~ 0.2',
            '2020': '0.01 ~ 0.8',
            '3000': '0.01 ~ 0.2',
            '3010': '0.01 ~ 0.4',
            '3020': '0.01 ~ 0.8'
        }.get(sizes, '')
        data['value3'] = pressure
        size = {
            '1000': '200',
            '1010': '300',
            '1020': '350',
            '2000': '600',
            '2010': '800',
            '2020': '1000',
            '3000': '3000',
            '3010': '4000',
            '3020': '5000'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_irxrt01(name, data, num_lines):
    # value3 - диапазон давления, value4 - расход, value6 - резьба
    pattern = r"IR(\d{4})-(F?\d{2})-XRT01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        pressure = {
            '1000': '0.005 ~ 0.2',
            '1010': '0.01 ~ 0.4',
            '1020': '0.01 ~ 0.8',
            '2000': '0.005 ~ 0.2',
            '2010': '0.01 ~ 0.4',
            '2020': '0.01 ~ 0.8',
            '3000': '0.005 ~ 0.2',
            '3010': '0.01 ~ 0.4',
            '3020': '0.01 ~ 0.8'
        }.get(sizes, '')
        data['value3'] = pressure
        size = {
            '1000': '510',
            '1010': '510',
            '1020': '510',
            '2000': '1030',
            '2010': '1030',
            '2020': '1030',
            '3000': '1640',
            '3010': '3100',
            '3020': '3650'
        }.get(sizes, '')
        data['value4'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_itvxkv01(name, data, num_lines):
    # value2 - макс давление, value3 - вых. давление, value4 - вх. сигнал
    # value5 - вых. сигнал, value6 - расход, value8 - резьба
    pattern = r"ITV(\d{4})-(\d{1})(\d{1})(F?\d{1}).+"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        inputes = str(match.group(2))  # Упр. сигнал
        outputes = str(match.group(3))  # Вых. сигнал
        threads = str(match.group(4))  # Резьба
        # Вставка 0 между перед последним символом
        threads = threads[:-1] + "0" + threads[-1]
        pressure = {
            '1010': '0.2',
            '1030': '1',
            '1050': '1',
            '2010': '0.2',
            '2030': '1',
            '2050': '1',
            '3010': '0.2',
            '3030': '1',
            '3050': '1'
        }.get(sizes, '')
        data['value2'] = pressure
        pressure2 = {
            '1010': '0.1',
            '1030': '0.5',
            '1050': '0.9',
            '2010': '0.1',
            '2030': '0.5',
            '2050': '0.9',
            '3010': '0.1',
            '3030': '0.5',
            '3050': '0.9'
        }.get(sizes, '')
        data['value3'] = pressure2
        input = {
            '0': 'Ток 4~20 мА',
            '1': 'Ток 0~20 мА',
            '2': 'Напряжение 0~5 VDC',
            '3': 'Напряжение 0~10 VDC'
        }.get(inputes, '')
        data['value4'] = input
        output = {
            '1': 'Аналоговый 1~5 VDC',
            '2': 'Релейный NPN',
            '3': 'Релейный PNP',
            '4': 'Аналоговый 4~20 мА'
        }.get(outputes, '')
        data['value5'] = output
        size = {
            '1010': '80',
            '1030': '120',
            '1050': '150',
            '2010': '500',
            '2030': '1150',
            '2050': '1000',
            '3010': '1500',
            '3030': '3000',
            '3050': '3500'
        }.get(sizes, '')
        data['value6'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value8'] = thread
    return num_lines


def data_update_itvxtp01(name, data, num_lines):
    # value2 - макс давление, value3 - вых. давление, value4 - вх. сигнал
    # value5 - вых. сигнал, value6 - расход, value8 - резьба
    pattern = r"ITV(\d{4})-(\d{1})(\d{1})(F?\d{1}).+"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        inputes = str(match.group(2))  # Упр. сигнал
        outputes = str(match.group(3))  # Вых. сигнал
        threads = str(match.group(4))  # Резьба
        # Вставка 0 между перед последним символом
        threads = threads[:-1] + "0" + threads[-1]
        pressure = {
            '1010': '0.2',
            '1030': '1',
            '1050': '1',
            '2010': '0.2',
            '2030': '1',
            '2050': '1',
            '3010': '0.2',
            '3030': '1',
            '3050': '1'
        }.get(sizes, '')
        data['value2'] = pressure
        pressure2 = {
            '1010': '0.1',
            '1030': '0.5',
            '1050': '0.9',
            '2010': '0.1',
            '2030': '0.5',
            '2050': '0.9',
            '3010': '0.1',
            '3030': '0.5',
            '3050': '0.9'
        }.get(sizes, '')
        data['value3'] = pressure2
        input = {
            '0': 'Ток 4~20 мА',
            '1': 'Ток 0~20 мА',
            '2': 'Напряжение 0~5 VDC',
            '3': 'Напряжение 0~10 VDC'
        }.get(inputes, '')
        data['value4'] = input
        output = {
            '1': 'Аналоговый 1~5 VDC',
            '2': 'Релейный NPN',
            '3': 'Релейный PNP',
            '4': 'Аналоговый 4~20 мА'
        }.get(outputes, '')
        data['value5'] = output
        size = {
            '1010': '80',
            '1030': '120',
            '1050': '150',
            '2010': '500',
            '2030': '1150',
            '2050': '1000',
            '3010': '1500',
            '3030': '3000',
            '3050': '3500'
        }.get(sizes, '')
        data['value6'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value8'] = thread

    pattern = r"ITV00(\d{2})-(\d{1})[A-Za-z]{2}.+"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        inputes = str(match.group(2))  # Упр. сигнал
        pressure = {
            '10': '0.2',
            '30': '1',
            '50': '1'
        }.get(sizes, '')
        data['value2'] = pressure
        pressure2 = {
            '10': '0.1',
            '30': '0.5',
            '50': '0.9'
        }.get(sizes, '')
        data['value3'] = pressure2
        input = {
            '0': 'Ток 4~20 мА',
            '1': 'Ток 0~20 мА',
            '2': 'Напряжение 0~5 VDC',
            '3': 'Напряжение 0~10 VDC'
        }.get(inputes, '')
        data['value4'] = input
        data['value5'] = 'Отсутствует'
        data['value6'] = '6'
        data['line8'] = 'Быстроразъемное соединение (мм)'
        data['value8'] = '4'
    return num_lines


def data_update_itvxxtp01(name, data, num_lines):
    # value4 - вх. сигнал, value5 - вых. сигнал, value8 - резьба
    pattern = r"ITVX2030-(\d{1})(\d{1})(F?\d{1}).+"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        inputes = str(match.group(1))  # Упр. сигнал
        outputes = str(match.group(2))  # Вых. сигнал
        threads = str(match.group(3))  # Резьба
        # Вставка 0 между перед последним символом
        threads = threads[:-1] + "0" + threads[-1]
        input = {
            '0': 'Ток 4~20 мА',
            '1': 'Ток 0~20 мА',
            '2': 'Напряжение 0~5 VDC',
            '3': 'Напряжение 0~10 VDC'
        }.get(inputes, '')
        data['value4'] = input
        output = {
            '1': 'Аналоговый 1~5 VDC',
            '2': 'Релейный NPN',
            '3': 'Релейный PNP',
            '4': 'Аналоговый 4~20 мА'
        }.get(outputes, '')
        data['value5'] = output
        thread = thread_not_fittings.get(threads, '')
        data['value8'] = thread
    return num_lines


def data_update_itv2090xtp01(name, data, num_lines):
    # value4 - вх. сигнал, value5 - вых. сигнал, value7 - резьба
    pattern = r"ITV2090-(\d{1})(\d{1})(F?\d{1}).+"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        inputes = str(match.group(1))  # Упр. сигнал
        outputes = str(match.group(2))  # Вых. сигнал
        threads = str(match.group(3))  # Резьба
        # Вставка 0 между перед последним символом
        threads = threads[:-1] + "0" + threads[-1]
        input = {
            '0': 'Ток 4~20 мА',
            '1': 'Ток 0~20 мА',
            '2': 'Напряжение 0~5 VDC',
            '3': 'Напряжение 0~10 VDC'
        }.get(inputes, '')
        data['value4'] = input
        output = {
            '1': 'Аналоговый 1~5 VDC',
            '2': 'Релейный NPN',
            '3': 'Релейный PNP',
            '4': 'Аналоговый 4~20 мА'
        }.get(outputes, '')
        data['value5'] = output
        thread = thread_not_fittings.get(threads, '')
        data['value7'] = thread
    return num_lines


def data_update_alxln01(name, data, num_lines):
    # value3 - расход, value5 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value5'] = thread
        # Условие для G3/4
        if sizes == '4000' and thread == 'G3/4':
            data['value3'] = '6300'
        if sizes == '5000' and thread == 'G3/4':
            data['value3'] = '7000'
    return num_lines


def data_update_alxrt01(name, data, num_lines):
    # value3 - расход, value5 - резьба
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
            '5000': '7000'
        }.get(sizes, '')
        data['value3'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value5'] = thread
        # Условие для G3/4
        if sizes == '4000' and thread == 'G3/4':
            data['value3'] = '6300'
    return num_lines


def data_update_vhsxln01(name, data, num_lines):
    # value3 - расход, value4 - расход выхлоп, value6 - резьба, value7 - резьба выхлоп
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
        # Условия по расходу
        if sizes == '2000':
            data['value3'] = '0.7'
            data['value4'] = '0.8'
        elif sizes == '3000':
            if thread == 'G1/4':
                data['value3'] = '0.8'
                data['value4'] = '0.7'
            elif thread == 'G3/8':
                data['value3'] = '1.7'
                data['value4'] = '1.6'
        elif sizes == '4000':
            if thread == 'G3/8':
                data['value3'] = '2'
                data['value4'] = '2'
            elif thread == 'G1/2':
                data['value3'] = '3'
                data['value4'] = '2'
        elif sizes == '5000':
            if thread == 'G3/4':
                data['value3'] = '4.3'
                data['value4'] = '2.9'
            elif thread == 'G1':
                data['value3'] = '6.7'
                data['value4'] = '2.9'
    return num_lines


def data_update_vhsxrt01(name, data, num_lines):
    # value3 - расход, value4 - расход выхлоп, value6 - резьба, value7 - резьба выхлоп
    pattern = r"VHS(\d{4})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size_exh = {
            '2000': 'Rc1/8',
            '3000': 'Rc1/4',
            '4000': 'Rc3/8'
        }.get(sizes, '')
        data['value7'] = size_exh
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
        # Условия по расходу
        if sizes == '2000':
            data['value3'] = '0.76'
            data['value4'] = '0.87'
        elif sizes == '3000':
            if thread == 'Rc1/4':
                data['value3'] = '0.87'
                data['value4'] = '0.76'
            elif thread == 'Rc3/8':
                data['value3'] = '1.68'
                data['value4'] = '1.57'
        elif sizes == '4000':
            if thread == 'Rc3/8':
                data['value3'] = '1.46'
                data['value4'] = '1.95'
            elif thread == 'Rc1/2':
                data['value3'] = '2.06'
                data['value4'] = '2.17'
    return num_lines


def data_update_acxln01(name, data, num_lines):
    # value5 - расход, value7 - резьба
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
            '5010': '4000'
        }.get(sizes, '')
        data['value5'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value7'] = thread
    return num_lines


def data_update_acxrt01(name, data, num_lines):
    # value5 - расход, value7 - резьба
    pattern = r"AC(\d{4})-(F?\d{2})(?:D)?-(.+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер
        threads = str(match.group(2))  # Резьба
        size = {
            '2000': '500',
            '3000': '2000',
            '4000': '4000',
            '5000': '5000',
            '2010': '500',
            '3010': '1700',
            '4010': '3000',
            '5010': '5000'
        }.get(sizes, '')
        data['value5'] = size
        thread = thread_not_fittings.get(threads, '')
        data['value7'] = thread
        if sizes == '4000' and thread == 'G3/4':
            data['value5'] = '4500'
    return num_lines


def data_update_amgxkv01(name, data, num_lines):
    # value3 - расход, value5 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value5'] = thread
    return num_lines


def data_update_affxkv01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_amxkv01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_amdxkv01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_amhxkv01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_amexkv01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_amfxkv01(name, data, num_lines):
    # value4 - расход, value6 - резьба
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
        thread = thread_not_fittings.get(threads, '')
        data['value6'] = thread
    return num_lines


def data_update_sy_20(name, data, num_lines):
    # value2 - диапазон давлений, value3 - расход, value4 - напряжение, value6 - резьба/БРС
    # 1 группа - типоразмер, 2 - тип распреда, 3 - напряжение, далее кусок не нужен и после черты уже присоединение
    pattern = r"SY(\d{1})(\d{1})20-(.)(?:.+)-(.+)-(?:.+)"
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        sizes = str(match.group(1))  # Типоразмер, не используется пока, оставил на всякий
        types = str(match.group(2))  # Тип
        voltages = str(match.group(3))  # Напряжение
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
    return num_lines


def data_update_kqg2xrt01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQG2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            if first_part == 'F':  # У KQG2F обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16']:
            num_lines += 1
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")
    return num_lines


def data_update_kqg2xln01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQG2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            if first_part == 'F':  # У KQG2F обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16']:
            num_lines += 1
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

    return num_lines


def data_update_kqg2xkv01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQG2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        if first_part in ['TF']:
            data['Name_product'] = str(data['Name_product']).replace('Фитинг', 'Коллектор')
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value5'] = thread

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16']:
            num_lines += 1
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

        # Обработка KQP
    pattern = r"KQG2P-(\d{2})-XKV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))
        data['value4'] = str(first_digits).lstrip("0")
    return num_lines


def data_update_kfgxnc01(name, data, num_lines):
    # value4/value5 - место для БРС, value6 - место для резьбы (если есть)
    pattern = r"KFG(?:.+)(\d{2})(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС1
        second_digits = str(match.group(2))  # БРС2
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        data['value5'] = str(second_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value6'] = thread

        if data['value5'] == '65':
            data['value5'] = '6.5'
    return num_lines


def data_update_kfgxrt01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KFG(?:.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС1
        second_group = str(match.group(2))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value5'] = thread
    return num_lines


def data_update_kfgxnt01(name, data, num_lines):
    # value4/value5 - место для БРС, value6 - место для резьбы (если есть)
    pattern = r"KFG(?:.+)(\d{2})(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС1
        second_digits = str(match.group(2))  # БРС2
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        data['value5'] = str(second_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value6'] = thread

        if data['value5'] == '25':
            data['value5'] = '2.5'
        elif data['value5'] == '75':
            data['value5'] = '7.5'

    return num_lines


def data_update_kqxrt02(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"([A-Z]+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            if first_part == 'KQLF' or first_part == 'KQF':  # У KQLF/KQF обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16', '14']:
            num_lines += 1
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

        # Условие для KQT06-04-XRT02 и подобных, здесь например 04 опознало как резьбу, а это БРС
        if '06-04' in name:
            # num_lines += 1 - здесь не увеличиваем кол-во строк, т.к. в 1 цикле зацепило по 04 и увеличило.
            # Сейчас повторно обрабатываем
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")
    # Обработка KQP
    pattern = r"KQP-(\d{2})"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))
        data['value4'] = str(first_digits).lstrip("0")
    return num_lines


def data_update_kq2xrt01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQ2(.+)(\d{2})-(.+)(?:A)?-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value5'] = thread

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16', '14']:
            num_lines += 1
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

    # Обработка KQP
    pattern = r"KQ2P-(\d{2})"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))
        data['value4'] = str(first_digits).lstrip("0")
    return num_lines


def data_update_kq2uxlc01(name, data, num_lines):
    #value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQ2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = {
                'U01': 'Uni1/8',
                'U02': 'Uni1/4',
                'U03': 'Uni3/8',
                'U04': 'Uni1/2'
            }.get(second_group, '')
            data['value5'] = thread
    return num_lines


def data_update_kqb2xrt01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQB2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            if first_part == 'F':  # У KQB2F обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16', '14']:
            num_lines += 1
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")
    return num_lines


def data_update_kqb2xln01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KQB2(.+)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            if first_part == 'F':  # У KQB2F обозначение резьб как R, а по факту G
                thread = thread.replace('R', 'G')
            data['value5'] = thread

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16', '14']:
            num_lines += 1
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")
    return num_lines


def data_update_kpksxrt01(name, data, num_lines):
    # value4 - основной параметр
    pattern = r"K.(.)(\d{2})-XRT01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # типоразмер
        if first_part == 'M':
            data['line4'] = 'Резьбовое присоединение'
            if first_digits == '10':
                data['value4'] = 'R1/8'
            elif first_digits == '20':
                data['value4'] = 'R1/4'
            elif first_digits == '30':
                data['value4'] = 'R3/8'
            elif first_digits == '40':
                data['value4'] = 'R1/2'
        elif first_part == 'F':
            data['line4'] = 'Резьбовое присоединение'
            if first_digits == '10':
                data['value4'] = 'G1/8'
            elif first_digits == '20':
                data['value4'] = 'G1/4'
            elif first_digits == '30':
                data['value4'] = 'Rc3/8'
            elif first_digits == '40':
                data['value4'] = 'G1/2'
        elif first_part == 'H':
            data['line4'] = 'Диаметр "ёлочки" (мм)'
            if first_digits == '10':
                data['value4'] = '7.2'
            elif first_digits == '20':
                data['value4'] = '9'
            elif first_digits == '30':
                data['value4'] = '11'
            elif first_digits == '40':
                data['value4'] = '13.2'
        elif first_part == 'P':
            data['line4'] = 'Диаметр трубки (мм)'
            if first_digits == '10':
                data['value4'] = '6'
            elif first_digits == '20':
                data['value4'] = '8'
            elif first_digits == '30':
                data['value4'] = '10'
            elif first_digits == '40':
                data['value4'] = '12'
    return num_lines


def data_update_kskxxrt01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы, value6 - скорость вращения
    pattern = r"K(.)(?:.)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        thread = thread_fittings.get(second_group, '')
        data['value5'] = thread
        if first_part == 'S':
            speed = {
                '04': '500',
                '06': '500',
                '08': '400',
                '10': '300',
                '12': '250'
            }.get(first_digits, '')
        elif first_part == 'X':
            speed = {
                '04': '1500',
                '06': '1200',
                '08': '1200',
                '10': '1000',
                '12': '1000'
            }.get(first_digits, '')
        data['value6'] = speed
    return num_lines


def data_update_ksxlc01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы, value6 - скорость вращения
    pattern = r"K(.)(?:.)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        thread = thread_fittings.get(second_group, '')
        data['value5'] = thread
        if first_part == 'S':
            speed = {
                '04': '500',
                '06': '500',
                '08': '400',
                '10': '300',
                '12': '250',
                '16': '200'
            }.get(first_digits, '')
        data['value6'] = speed
    return num_lines


def data_update_kcxrt01(name, data, num_lines):
    # value4 - место для БРС, value5 - место для резьбы (если есть)
    pattern = r"KC(.)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1))  # Серия фитинга
        first_digits = str(match.group(2))  # БРС
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value5'] = thread
    return num_lines


def data_update_kprxjc01(name, data, num_lines):
    # value4/value5 - место для БРС, value6 - место для резьбы (если есть)
    pattern = r"KPR(?:.*)(\d{2})(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС1
        second_digits = str(match.group(2))  # БРС2
        second_group = str(match.group(3))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        data['value5'] = str(second_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value6'] = thread

        if second_group in ['NUT']:
            data['Name_product'] = 'Накидная гайка'

        if data['value5'] == '25':
            data['value5'] = '2.5'
    return num_lines


def data_update_kfxrt01(name, data, num_lines):
    # value4/value5 - место для БРС, value6 - место для резьбы (если есть)
    pattern = r"K.F.(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС1
        second_group = str(match.group(2))  # БРС/резьба
        inner_tube = {
            '04': '2.5',
            '06': '4',
            '08': '5',
            '10': '6.5',
            '12': '8'
        }.get(first_digits, '')
        data['value4'] = str(first_digits).lstrip("0")
        data['value5'] = inner_tube
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value6'] = thread
    return num_lines


def data_update_hdxrt01(name, data, num_lines):
    # value4, value5 - место для резьбы (если есть)
    pattern = r"(?:.*)(\d{2})-(.+)-([A-Z]+)"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_digits = str(match.group(1))  # БРС
        second_group = str(match.group(2))  # БРС/резьба
        data['value4'] = str(first_digits).lstrip("0")
        # Сейчас обработаем резьбовые фитинги
        #  Если будет резьба, нужно добавить 1 строчку в таблицу
        have_thread = contains_any_substring(second_group, little_thread)
        if have_thread:
            num_lines += 1
            thread = thread_fittings.get(second_group, '')
            data['value5'] = thread
    return num_lines


def data_update_txrt01(name, data, num_lines):
    # value2 - давление, value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^T(\d{2})(\d{2}).+-XRT01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        elif data['value4'] == '75':
            data['value4'] = '7.5'
        pressure = {
            '04': '3.3',
            '06': '3',
            '08': '2',
            '10': '2',
            '12': '2',
            '16': '1.6'
        }.get(out_diam, '')
        data['value2'] = pressure
        radius = {
            '04': '25',
            '06': '45',
            '08': '60',
            '10': '75',
            '12': '100',
            '16': '200'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tsxln01(name, data, num_lines):
    # value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TS(\d{2})(\d{2}).+-XLN01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        elif data['value4'] == '75':
            data['value4'] = '7.5'
        radius = {
            '04': '25',
            '06': '45',
            '08': '60',
            '10': '75',
            '12': '100'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tsxnv012(name, data, num_lines):
    # value2 - давление, value3 - внеш диам, value4 - внут диам, value5 - температура, value6 - рад изгиба
    pattern = r"^TS(\d{2})(\d{2}).+-XNV(\d{2})"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        end = str(match.group(3))  # Концовка, отвечает за материал
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        elif data['value4'] == '75':
            data['value4'] = '7.5'

        if end == '01':
            data['value5'] = '-40 ~ +125'
            data['value2'] = '2'
        elif end == '02':
            data['value5'] = '-40 ~ +100'
            if out_diam == '10' and inner_diam == '08':
                data['value2'] = '1.5'
            elif out_diam == '12' and inner_diam == '10':
                data['value2'] = '1.5'
            elif out_diam == '16' and inner_diam == '12':
                data['value2'] = '1.5'
            else:
                data['value2'] = '2'
        all_diam = out_diam + inner_diam
        if end == '01':
            radius = {
                '0425': '25',
                '0604': '45',
                '0806': '60',
                '1008': '90',
                '1075': '75',
                '1209': '100',
                '1210': '140',
                '1411': '130',
                '1612': '180'
            }.get(all_diam, '')
        elif end == '02':
            radius = {
                '0425': '15',
                '0604': '20',
                '0806': '30',
                '1008': '45',
                '1075': '40',
                '1209': '50',
                '1210': '55',
                '1612': '105'
            }.get(all_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tuxrt01(name, data, num_lines):
    # value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TU(\d{2})(\d{2}).+-XRT01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        elif data['value4'] == '65':
            data['value4'] = '6.5'
        radius = {
            '04': '10',
            '06': '15',
            '08': '20',
            '10': '25',
            '12': '37',
            '16': '60'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tuxln01(name, data, num_lines):
    # value2 - давление, value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TU(\d{2})(\d{2}).+-XLN01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        elif data['value4'] == '65':
            data['value4'] = '6.5'
        radius = {
            '04': '10',
            '06': '15',
            '08': '20',
            '10': '30',
            '12': '35',
            '16': '65'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tuxnv01(name, data, num_lines):
    # value2 - давление, value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TU(\d{2})(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        elif data['value4'] == '65':
            data['value4'] = '6.5'
        elif data['value4'] == '12':
            data['value4'] = '1.2'
        all_diam = out_diam + inner_diam
        if all_diam == '0806':
            data['value2'] = '0.7'
        elif all_diam == '1008':
            data['value2'] = '0.6'
        elif all_diam in ['1209', '1410', '1612']:
            data['value2'] = '0.8'
        radius = {
            '0212': '8',
            '0302': '10',
            '0425': '10',
            '0604': '15',
            '0805': '20',
            '0806': '30',
            '1065': '30',
            '1008': '38',
            '1208': '35',
            '1209': '40',
            '1410': '55',
            '1612': '65'
        }.get(all_diam, '')
        data['value6'] = radius
    pattern = r"^TIUB(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        data['line3'] = 'Внешний диаметр, дюймы (мм)'
        diam = str(match.group(1))  # Диаметр
        out_diam = {
            '07': '1/4" (6.35 мм)',
            '11': '3/8" (9.52 мм)',
            '13': '1/2" (12.7 мм)'
        }.get(diam, '')
        data['value3'] = out_diam
        inner_diam = {
            '07': '4.23',
            '11': '6.35',
            '13': '8.46'
        }.get(diam, '')
        data['value4'] = inner_diam
        radius = {
            '07': '15',
            '11': '30',
            '13': '35'
        }.get(diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tpexnv01(name, data, num_lines):
    # value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TPE(\d{2})(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        elif data['value4'] == '75':
            data['value4'] = '7.5'
        radius = {
            '04': '10',
            '06': '15',
            '08': '20',
            '10': '30',
            '12': '35'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tcuxnv01(name, data, num_lines):
    #1 артикул, функция обработчик не нужна, но оставил чтобы логику программы не нарушать
    return num_lines


def data_update_stuxln01(name, data, num_lines):
    # value3 - внеш диам, value4 - внут диам, value6 - вся длина, value7 - раб длина
    pattern = r"^STU(\d{2})(\d{2})[A-Za-z]{1,2}-(\d{1,2})-XLN01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        lenght = str(match.group(3))  # Полная длина
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        elif data['value4'] == '65':
            data['value4'] = '6.5'
        data['value6'] = lenght
        work_lenght = {
            '2': '1',
            '3': '1.5',
            '5': '2.5',
            '7': '3.5',
            '10': '5',
            '14': '7',
            '20': '10'
        }.get(lenght, '')
        data['value7'] = work_lenght
    return num_lines


def data_update_tpfaxkv01(name, data, num_lines):
    # value2 - давление, value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TPFA(\d{2})(\d{2}).+-XKV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        pressure = {
            '04': '1.7',
            '06': '1.5',
            '08': '1',
            '10': '0.7',
            '12': '0.6'
        }.get(out_diam, '')
        data['value2'] = pressure
        radius = {
            '04': '20',
            '06': '35',
            '08': '60',
            '10': '100',
            '12': '130'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tptfexnv01(name, data, num_lines):
    # value2 - давление, value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TPTFE(\d{2})(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '25':
            data['value4'] = '2.5'
        all_diam = out_diam + inner_diam
        pressure = {
            '0402': '2.5',
            '0425': '1.6',
            '0403': '0.9',
            '0604': '1.3',
            '0806': '0.85',
            '1008': '0.65',
            '1209': '0.75',
            '1210': '0.5',
            '1613': '0.55',
            '1916': '0.45',
            '2522': '0.35'
        }.get(all_diam, '')
        data['value2'] = pressure
        radius = {
            '0402': '15',
            '0425': '25',
            '0403': '35',
            '0604': '35',
            '0806': '65',
            '1008': '100',
            '1209': '105',
            '1210': '150',
            '1613': '190',
            '1916': '265',
            '2522': '430'
        }.get(all_diam, '')
        data['value6'] = radius
    pattern = r"^TIPTFE(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        diam = str(match.group(1))  # Диаметр
        pressure = {
            '01': '2.4',
            '07': '1.5',
            '11': '1.15',
            '13': '0.8',
            '19': '0.45',
            '25': '0.4'
        }.get(diam, '')
        data['value2'] = pressure
        data['line3'] = 'Внешний диаметр, дюймы'
        out_diam = {
            '01': '1/8"',
            '07': '1/4"',
            '11': '3/8"',
            '13': '1/2"',
            '19': '3/4"',
            '25': '1"'
        }.get(diam, '')
        data['value3'] = out_diam
        data['line4'] = 'Толщина стенки, дюймы'
        thin = {
            '01': '0.03"',
            '07': '0.047"',
            '11': '0.062"',
            '13': '0.062"',
            '19': '0.062"',
            '25': '0.062"'
        }.get(diam, '')
        data['value4'] = thin
        radius = {
            '01': '15',
            '07': '35',
            '11': '60',
            '13': '115',
            '19': '250',
            '25': '430'
        }.get(diam, '')
        data['value6'] = radius
    return num_lines


def data_update_trbuxkv01(name, data, num_lines):
    #  value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TRBU(\d{2})(\d{2}).+-XKV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '65':
            data['value4'] = '6.5'
        radius = {
            '06': '15',
            '08': '20',
            '10': '30',
            '12': '45'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_trbuxnv01(name, data, num_lines):
    #  value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TRBU(\d{2})(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '65':
            data['value4'] = '6.5'
        elif data['value4'] == '25':
            data['value4'] = '2.5'
        radius = {
            '04': '10',
            '06': '15',
            '08': '20',
            '10': '30',
            '12': '45',
            '16': '60'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_trtuxnv01(name, data, num_lines):
    #  value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TRTU(\d{2})(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '65':
            data['value4'] = '6.5'
        radius = {
            '06': '15',
            '08': '20',
            '10': '30',
            '12': '45',
            '14': '75'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tauxnv01(name, data, num_lines):
    #  value3 - внеш диам, value4 - внут диам, value6 - рад изгиба
    pattern = r"^TAU(\d{2})(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '65':
            data['value4'] = '6.5'
        elif data['value4'] == '25':
            data['value4'] = '2.5'
        radius = {
            '04': '10',
            '06': '15',
            '08': '25',
            '10': '35',
            '12': '45'
        }.get(out_diam, '')
        data['value6'] = radius
    return num_lines


def data_update_tudlxnv01(name, data, num_lines):
    #  value3 - внеш диам, value4 - внут диам
    pattern = r"^TUDL(\d{2})(\d{2}).+-XNV01"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        out_diam = str(match.group(1))  # Внешний диаметр
        inner_diam = str(match.group(2))  # Внутренний диаметр
        data['value3'] = str(out_diam).lstrip("0")
        data['value4'] = str(inner_diam).lstrip("0")
        if data['value4'] == '65':
            data['value4'] = '6.5'
    return num_lines