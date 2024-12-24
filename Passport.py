from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
import configparser
import re
import tkinter as tk

name = ""  # Глобальная переменная для хранения введенного значения

def paste(event):
    if event.keysym == 'v' and (event.state & 0x0004):  # Проверяем, что нажаты Control
        try:
            clipboard_text = root.clipboard_get()
            if clipboard_text:  # Проверяем, что буфер обмена не пуст
                entry.delete(0, tk.END)  # Удаляем текущее содержимое поля ввода
                entry.insert(0, clipboard_text)  # Вставляем текст из буфера обмена
        except tk.TclError:
            pass  # Игнорируем ошибку, если буфер обмена пуст
        return 'break'  # Останавливаем дальнейшее распространение события

def get_input():
    global name
    name = entry.get()
    print(f"Введенный артикул: {name}")
    root.destroy()  # Закрываем окно после получения значения

root = tk.Tk()
root.title("Ввод артикула")  # Заголовок окна

label = tk.Label(root, text="Введите артикул:")
label.pack(padx=200, pady=30)

entry = tk.Entry(root)
entry.pack(padx=100, pady=10)

button = tk.Button(root, text="Подтвердить", command=get_input)
button.pack(padx=10, pady=10)

# Отключаем стандартную обработку события <Control-v>
entry.bind_class('Entry', '<Control-v>', lambda event: 'break')

# Привязываем нашу функцию paste к событию <Control-v>
entry.bind('<KeyPress>', paste)

root.mainloop()

# Загружаем существующий шаблон .docx
document = Document('template_SMCpart.docx')

# Получаем данные от пользователя
#name = input("Введите имя: ") - ввод с консоли

# Список шаблонов и соответствующих им имен конфигов
patterns_and_names = {
    r'KQ.*XLN01': 'KQ_XLN01.txt',
    r'KQ.*XRT01': 'KQ_XRT01.txt',
    r'KQ.*XRT02': 'KQ_XRT02.txt'
}

# Глобальная переменная для хранения имени конфигурации
config_name = ''

# Проверка соответствия и установка имени конфигурации
for pattern, config in patterns_and_names.items():
    if re.match(pattern, name):
        config_name = config
        break
else:
    print(f"Текст '{name}' не соответствует ни одному из шаблонов.")

# Выводим установленное имя конфигурации
print(f"Имя конфигурации: {config_name}")

config = configparser.ConfigParser()

# Указываем разделитель между ключами и значениями
config.optionxform = str  # Это важно, чтобы ключи оставались без изменений

# Читаем файл
try:
    with open(config_name, encoding='utf-8') as file:
        config.read_file(file)
except FileNotFoundError:
    print(f"Файл конфигурации {config_name} не найден.")

# Получаем значения из секции DEFAULT
try:
    data = dict(config['DEFAULT'])
except KeyError:
    print("Секция DEFAULT не найдена в файле конфигурации.")

print(data)

#Вспомогательная функция для определения наличия выражения в строке. Например, я сопоставляю, есть ли 01, 02, 03 в строках 01, G01, 02S и т.д.
def contains_any_substring(long_string, substrings):
    for substring in substrings:
        if substring in long_string:
            return True
    return False

num_lines = int(data['Number_lines'])

if config_name == 'KQ_XLN01.txt':
    pattern = r"([A-Z]+)(\d{2})-(.+)-([A-Z]+)" # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        # Извлекаем группы
        first_part = str(match.group(1)) #Серия фитинга
        first_digits = str(match.group(2)) #БРС
        second_group = str(match.group(3)) #БРС/резьба
        #Сейчас обработаем резьбовые фитинги
        substrings = ['01', '02', '03', '04', 'M3', 'M5', 'M6']
        have_rezba = contains_any_substring(second_group, substrings)
        if first_part in ['KQH', 'KQS', 'KQF', 'KQL', 'KQW', 'KQK', 'KQV', 'KQT', 'KQY',
                          'KQVF', 'KQU', 'KQLF'] and have_rezba:
            num_lines +=1
            if first_digits == '16':
                data['value2'] = str(0.8)
            data['value4'] = str(first_digits).lstrip("0")
            rezba = {
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
            if first_part == 'KQLF': #У KQLF обозначение резьб как R, а по факту G
                rezba = rezba.replace('R', 'G')
            data['value5'] = rezba
            print('ДА')

        #Условия для фитингов БРС
        if second_group in ['99', '00']:
            print('ДА0')
            if first_digits == '16':
                data['value2'] = str(0.8)
            data['value4'] = str(first_digits).lstrip("0")

        # Условия для фитингов БРС с разными выходами
        if second_group in ['06', '08', '10', '12', '16', '14']:
            print('ДА1')
            num_lines += 1
            if first_digits == '16':
                data['value2'] = str(0.8)
            data['value4'] = str(first_digits).lstrip("0")
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")

        # Условие для KQW03-M3-XLN01 и подобных
        if '06-04' in name:
            print('ДА2')
            #num_lines += 1 - здесь не увеличиваем кол-во строк, т.к. в 1 цикле зацепило по 04 и увеличило. Сейчас повторно обрабатываем
            data['value4'] = str(first_digits).lstrip("0")
            data['line5'] = data['line4']
            data['value5'] = str(second_group).lstrip("0")
    #Обработка KQP
    pattern = r"KQP(\d{2})"  # Вытаскиваем куски до и после черты для определения размеров
    match = re.search(pattern, name)
    if match:
        print('ДА3')
        # Извлекаем группы
        first_digits = str(match.group(1))
        data['value4'] = str(first_digits).lstrip("0")



def replace_text(run, old_text, new_text):
    if old_text in run.text:
        run.text = run.text.replace(old_text, new_text)

def format_text_onright(paragraph):
    for run in paragraph.runs:
        if run.text != "":
            run.font.name = 'Arial'
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0, 0, 0)
            paragraph.alignment = 2

def format_text_onleft(paragraph):
    for run in paragraph.runs:
        if run.text != "":
            run.font.name = 'Arial'
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0, 0, 0)
            paragraph.alignment = 0

for paragraph in document.paragraphs:
    if 'Declaration' in paragraph.text:
        for run in paragraph.runs:
            if data['Declaration'] == "-":
                replaced_run = replace_text(run, run.text, "")


for table in document.tables:
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    #run.text.replace('\r\n', '\n').replace('\r', '\n')
                    if 'Name_product' in run.text:
                        replaced_run = replace_text(run, run.text, data['Name_product'])
                        format_text_onright(paragraph)
                        break
                    if 'name' in run.text:
                        replaced_run = replace_text(run, run.text, name)
                        format_text_onright(paragraph)
                        break

                    for i in range(1, num_lines+1):
                        line_key = f'line{i}'
                        value_key = f'value{i}'
                        if line_key in run.text:
                            replaced_run = replace_text(run, run.text, data[line_key])
                            format_text_onleft(paragraph)
                            break
                        if value_key in run.text:
                            replaced_run = replace_text(run, run.text, data[value_key])
                            format_text_onright(paragraph)
                            break

                    for i in range(num_lines + 1, 9):
                        line_key = f'line{i}'
                        value_key = f'value{i}'
                        if line_key in run.text:
                            replaced_run = replace_text(run, run.text, '')
                            break
                        if value_key in run.text:
                            replaced_run = replace_text(run, run.text, '')
                            break


document.save(name + '.docx')
print("Документ успешно заполнен!")