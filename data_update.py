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
