import datetime as dt
import json
import schedule
import time
import logging
import os
import telegrambot

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from deepdiff import DeepDiff


def find_previous_file(current_str_date):
    """Поиск предыдущего файла по имени"""

    # Получаем дату и время из имени текущего файла
    current_datetime = dt.datetime.strptime(current_str_date, '%Y_%m_%d_%H')
    
    # Вычисляем дату и время предыдущего файла
    previous_datetime = current_datetime - dt.timedelta(hours=3)
    
    # Форматируем дату и время предыдущего файла обратно в строку
    previous_file_name = previous_datetime.strftime('%Y_%m_%d_%H_list') + '.json'
    
    # Ищем предыдущий файл в директории
    for file_name in os.listdir('./data'):
        if file_name.startswith(previous_file_name):
            print(file_name)
            return file_name
    
    # Если предыдущий файл не найден, возвращаем None
    return None


def compare_json_files(current_json, current_str_date):
     """Сравнение текущего json файла с предыдущим"""

     # Найти прошлый json файл по дате
     previous_file = find_previous_file(current_str_date) 
     if previous_file is None:
          return {}

     # Открываем два JSON-файла и загружаем их содержимое в объекты Python
     with open(f'./data/{previous_file}', 'r', encoding='utf-8') as prev_file, open(current_json, 'r', encoding='utf-8') as cur_file:
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

     # # Запись в файл json
     # with open(f'./data/changes_list.json', "w", encoding="utf-8") as file:
     #      json.dump(new_diff, file, indent=4, ensure_ascii=False)

     # Возвращаем словарь
     return new_diff


def send_telegram_message():
     pass


def parse():
     """Функция, для парсинга сайта sbermegamarket"""
     logging.info(f'{dt.datetime.now()}: Старт парсинга')
     
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

     url = "https://sbermegamarket.ru/catalog/sushilnye-mashiny/#?filters=%7B%224CB2C27EAAFC4EB39378C4B7487E6C9E%22%3A%5B%221%22%5D%2C%222B0B1FF4756D49CF84B094522D57ED3D%22%3A%5B%22Haier%22%5D%7D"

     driver.get(url)

     html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
     
     # Определяем текущую дату и время (без минут)
     str_now = dt.datetime.now().replace(minute=0, second=0, microsecond=0).strftime("%Y_%m_%d_%H")
     
     # Проверка директории на существование
     if not os.path.exists('./data'):
          os.makedirs('./data')

     with open(f'./data/{str_now}_index.html', "w", encoding="utf-8") as file:
          file.write(html)

     with open(f'./data/{str_now}_index.html', "r", encoding="utf-8") as file:
          html = file.read()

     soup = BeautifulSoup(html, 'lxml')

     catalogs = soup.find('div', class_='catalog-listing__items catalog-listing__items_divider')

     # Получить список всех дочерних элементов div
     elements = catalogs.find_all('div', recursive=False)

     element_list = []

     # Пройтись по каждому дочернему элементу и получить его атрибуты и содержимое
     for element in elements:
          id = element.find("div", class_="item-title").find("a").get("data-product-id")
          title = element.find("div", class_="item-title").find("a").get("title")
          website = "https://sbermegamarket.ru" + element.find("div", class_="item-title").find("a").get("href")
          price = element.find("div", class_="item-price").find("span").text
          price = ''.join(filter(str.isdigit, price))
          bonus_amount = element.find("span", class_="bonus-amount").text
          
          element_list.append(
               {
                    "id": id,
                    "title": title,
                    "website": website,
                    "price": price,
                    "bonus_amount": bonus_amount
               }
          )
     # Запись в файл json
     with open(f'./data/{str_now}_list.json', "w", encoding="utf-8") as file:
          json.dump(element_list, file, indent=4, ensure_ascii=False)
     
     logging.info(f'{dt.datetime.now()}: Завершение парсинга')

     os.remove(f'./data/{str_now}_index.html')

     # Находим расхождения с предыдущим файлом
     diff = compare_json_files(file.name, str_now)

     if diff:
          send_telegram_message()

     print(diff)
     

def main():
     """Задаем расписание и выполнение парсинга"""
     
     # Настройка логгера
     logging.basicConfig(filename='./logs/myapp.log', level=logging.INFO, encoding='utf-8')

     logging.info(f'{dt.datetime.now()}: Запуск приложения')
     
     # Запуска телеграм бота
     bot = telegrambot.TelegramBot("6303995867:AAH8Bq5pfu7RDW8YZ5Y7DJg0DwgiruClu0A")
     bot.run()

     # Первоначальный запуск парсинга
     parse()
     
     # Задаем расписание выполнения задачи раз в час
     schedule.every(3).hours.do(parse)

     # Бесконечный цикл, который выполняет код каждый час
     while True:
          logging.info(f'{dt.datetime.now()}: Следующая итерация')
          schedule.run_pending()
          time.sleep(60 * 30)

if __name__ == "__main__":
    main()
