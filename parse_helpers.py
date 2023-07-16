import datetime as dt
import json
import os
import requests

from deepdiff import DeepDiff
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def check_link(link):
    """Функция проверяет работуспособность полученной ссылки"""
    try:
        requests.get(link)
        return True
    except requests.ConnectionError:
        return False


def generate_bot_message(diff):
    """Генерация сообщения исходя из словаря изменений"""
    message = ""
    for key, value in diff.items():
        if "price" in value:
            field = "Цена"
            new_value = value["price"]["new_value"]
            old_value = value["price"]["old_value"]

            message += f"Изменились {field}:\n"
            message += f"Старая цена: {old_value}\n"
            message += f"Новая цена: {new_value}\n\n"

        if "bonus_amount" in value:
            field = "Бонусы"
            new_bonus = value["bonus_amount"]["new_value"]
            old_bonus = value["bonus_amount"]["old_value"]

            message += f"Изменились {field}:\n"
            message += f"Старый бонус: {old_bonus}\n"
            message += f"Новый бонус: {new_bonus}"

    return message


def find_previous_file(current_str_date, market):
    """Поиск предыдущего файла по имени"""

    # Получаем дату и время из имени текущего файла
    current_datetime = dt.datetime.strptime(current_str_date, '%Y_%m_%d_%H')

    # Вычисляем дату и время предыдущего файла
    previous_datetime = current_datetime - dt.timedelta(hours=3)

    # Форматируем дату и время предыдущего файла обратно в строку
    previous_file_name = previous_datetime.strftime('%Y_%m_%d_%H_') + market + '_list.json'

    # Ищем предыдущий файл в директории
    for file_name in os.listdir('./data'):
        if file_name.startswith(previous_file_name):
            return file_name

    # Если предыдущий файл не найден, возвращаем None
    return None


def compare_json_files(current_json, current_str_date, market):
    """Сравнение текущего json файла с предыдущим"""

    # Найти прошлый json файл по дате
    previous_file = find_previous_file(current_str_date, market)
    if previous_file is None:
        return {}

    # Открываем два JSON-файла и загружаем их содержимое в объекты Python
    with open(f'./data/{previous_file}', 'r', encoding='utf-8') as prev_file, open(current_json, 'r',
                                                                                   encoding='utf-8') as cur_file:
        cur_json = json.load(cur_file)
        rev_json = json.load(prev_file)

    # Используем DeepDiff для нахождения различий между объектами
    diff = DeepDiff(rev_json, cur_json, ignore_order=True, verbose_level=2)

    # Получаем только измененные данные
    changes = diff.get("values_changed")

    # Создаем новый словарь различий с переработанной структурой
    new_diff = {}
    for key, value in changes.items():
        if key.startswith("root["):
            parts = key.split("[")
            index = int(parts[1].split("]")[0])
            new_key = parts[2].strip("'][").replace("'", "")
            if index not in new_diff:
                new_diff[index] = {}
            new_diff[index][new_key] = value

    # Возвращаем словарь
    return new_diff


def get_settings_driver():
    """Получаем настройки драйвера для перехода по ссылке"""
    # Настройки для запуска Chrome в headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # Устанавливаем пользовательский агент
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.2.625 Yowser/2.5 Safari/537.36'

    chrome_options.add_argument(f'user-agent={user_agent}')

    service = webdriver.chrome.service.Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver
