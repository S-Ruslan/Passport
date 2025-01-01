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
    return(num_lines)

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