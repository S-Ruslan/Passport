from docx import Document
from docx.shared import Pt, RGBColor
from datetime import datetime
from data_update import *
import configparser
import re
import tkinter as tk

# Общая логика работы программы
# Создаем интерфейс с кнопками и полями, привязываем к кнопке функцию обработке полей и запуск основной программы
# Определяется используемый шаблон паспорта (выбирался на начальном поле),
# далее этот docx шаблон подцепляется программой и в нем будут происходить все изменения (размеченные поля заменяются
# на характеристики продукции)
# Далее введенный артикул с помощью регулярных выражений соотносится к серии продукции и на основе этой серии
# загружается заранее созданный вручную конфигурационный фаил с основными характеристиками серии
# Т.к. внутри серии характеристики могут отличаться разных артикулов, сделаны специальные функции обработчики и
# выделены в отдельный фаил. Результат их работы - обновленный словарь, где ключами служат метки в docx и конфигураторе,
# а значения - то что должно быть вписано вместо меток. Метки одинаковы в обоих фаилах
# далее просто обновляем загруженный в начале docx шаблон и производим все замены внутри фаила по циклу
# согласно обновленному словарю, есть функции форматирования текста

# Известные уязвимости:
# Отсутствуют какие-либо проверки на кривость введенных выражений, подразумевается, что артикулы будут 100% корректны
# и взяты из CRM. Не писал, ибо нет задачи исправлять пользователей, актуально максимально расширить конфиг. фаилы

# Известные баги:
# В полях почему то не работает ctrl+v при русской раскладке клавиатуры. На англ. норм, решить проблему на
# текущий момент не смог
#

# создание глобаных переменных для работы с полями интерфейса
name = ""
passport_number = ""
executor = ""
company = ""
data = []
num_lines = 0


def replace_text(run, old_text, new_text):
    if old_text in run.text:
        run.text = run.text.replace(old_text, new_text)


# Форматирование текста в правый край (для правой части таблицы)
def format_text_onright(paragraph):
    for run in paragraph.runs:
        if run.text != "":
            run.font.name = 'Arial'
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0, 0, 0)
            paragraph.alignment = 2


# Форматирование текста в левый край (для левой части таблицы)
def format_text_onleft(paragraph):
    for run in paragraph.runs:
        if run.text != "":
            run.font.name = 'Arial'
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0, 0, 0)
            paragraph.alignment = 0


# функция обработчик нажатия на кнопку
def get_input():
    # объявление глобальных переменных (для считывания с окна ввода)
    global name, passport_number, executor, selected_company
    name = entry_name.get()
    passport_number = entry_passport.get()
    executor = entry_executor.get()
    # запуск основного кода программы
    run_main_code()


def run_main_code():
    # Загружаем существующий шаблон .docx
    if selected_company.get() == "SMC":
        document = Document('template_SMCpart.docx')
    elif selected_company.get() == "Indutech":
        document = Document('template_INDUTECHpart.docx')

    # Список шаблонов и соответствующих им имен конфигов
    patterns_and_names = {
        r'KQ.*XLN01': 'KQ_XLN01.txt',
        r'KQ.*XRT01': 'KQ_XRT01.txt',
        r'KQ.*XRT02': 'KQ_XRT02.txt'
    }

    # Переменная для хранения имени конфигурации
    config_name = ''

    # Проверка соответствия и установка имени конфигурации
    for pattern, config in patterns_and_names.items():
        if re.match(pattern, name):
            config_name = config
            break
    else:
        print(f"Текст '{name}' не соответствует ни одному из шаблонов.")

    config = configparser.ConfigParser()
    # Указываем разделитель между ключами и значениями
    config.optionxform = str
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

    num_lines = int(data['Number_lines'])

    if config_name == 'KQ_XLN01.txt':
        # Здесь странный код, суть - нужно обновить словарь и кол-во строк для вывода
        # словарь data обновляется нормально (Mutable объект), а счетчик строк (num_lines) обновляться не хочет
        # теоретически, можно поиграть с объявлением global, но возникают конфликты. Поэтому сделал так:
        # сама функция при работе обновляет словарь и возвращает в довесок обновленное кол-во строк
        num_lines = data_update_kqxln01(name, data, num_lines)

    # Ниже пошла обработка шаблона и замена полей
    for paragraph in document.paragraphs:
        if 'Declaration' in paragraph.text:
            for run in paragraph.runs:
                if data['Declaration'] == "-":
                    replace_text(run, run.text, "")
                else:
                    dec_string = (f"Продукция имеет\nДекларацию о соответствии\n{data['Declaration']}\n"
                                  f"сроком с {data['DS']} по {data['DE']}")
                    replace_text(run, run.text, dec_string)
                    run.font.name = 'Arial Narrow'
                    run.font.size = Pt(12)
                    run.font.color.rgb = RGBColor(0, 0, 0)
                    paragraph.alignment = 0
                    run.font.bold = True
                    break

    for paragraph in document.paragraphs:
        if 'Maker' in paragraph.text:
            for run in paragraph.runs:
                # Получаем текущее время
                current_time = datetime.now()
                # Извлекаем год, месяц и день
                year = current_time.year
                month = current_time.month
                day = current_time.day
                new_string = f"№{year}.{month}.{day}\\{executor}\\{passport_number} от {day}.{month}.{year}"
                replace_text(run, run.text, new_string)
                break

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        if 'Name_product' in run.text:
                            replace_text(run, run.text, data['Name_product'])
                            format_text_onright(paragraph)
                            break
                        if 'name' in run.text:
                            replace_text(run, run.text, name)
                            format_text_onright(paragraph)
                            break

                        for i in range(1, num_lines + 1):
                            line_key = f'line{i}'
                            value_key = f'value{i}'
                            if line_key in run.text:
                                replace_text(run, run.text, data[line_key])
                                format_text_onleft(paragraph)
                                break
                            if value_key in run.text:
                                replace_text(run, run.text, data[value_key])
                                format_text_onright(paragraph)
                                break

                        # удаление неиспользуемых ячеек(очистка от значений). В идеале в таблице просто удалять из нее
                        # все лишние строки, но придумать как это сделать не удалось. Думал сформировать таблицу
                        # силами программы и в нее вставлять, но как то все очень криво работало, сделал такой вариант
                        for i in range(num_lines + 1, 9):
                            line_key = f'line{i}'
                            value_key = f'value{i}'
                            if line_key in run.text:
                                replace_text(run, run.text, '')
                                break
                            if value_key in run.text:
                                replace_text(run, run.text, '')
                                break

    document.save(name + '.docx')
    output_text.delete('1.0', tk.END)  # Очищаем поле вывода перед новой записью
    output_text.insert(tk.END, 'Программа успешно отработала!\n')  # Сообщение об успехе


# Создаем главное окно приложения
root = tk.Tk()
root.title("Ввод данных")

# Поле для ввода артикула
label_name = tk.Label(root, text="Артикул:")
label_name.pack(anchor='w')
entry_name = tk.Entry(root, width=20)
entry_name.pack(anchor='w', fill='x')

# Поле для ввода номера паспорта
label_passport = tk.Label(root, text="Номер паспорта:")
label_passport.pack(anchor='w')
entry_passport = tk.Entry(root, width=10)
entry_passport.pack(anchor='w', fill='x')

# Поле для ввода исполнителя
label_executor = tk.Label(root, text="Исполнитель:")
label_executor.pack(anchor='w')
entry_executor = tk.Entry(root, width=10)
entry_executor.pack(anchor='w', fill='x')

# Переменная для хранения выбранного значения
selected_company = tk.StringVar()
selected_company.set("SMC")  # По умолчанию выбираем SMC

# Радиокнопки для выбора компании
radio_smc = tk.Radiobutton(root, text="SMC", variable=selected_company, value="SMC")
radio_smc.pack(anchor='w')

radio_indutech = tk.Radiobutton(root, text="Индутех", variable=selected_company, value="Indutech")
radio_indutech.pack(anchor='w')

# Поле вывода результата
output_text = tk.Text(root, height=8, width=40)
output_text.pack(anchor='w')

# Кнопка подтверждения
button_confirm = tk.Button(root, text="Подтвердить", command=get_input)
button_confirm.pack(pady=(10, 0))

root.mainloop()
