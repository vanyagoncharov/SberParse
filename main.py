import datetime as dt
import json
import schedule
import time
import logging
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Функция, которая выполняет код
def parse():
    logging.info(f'{dt.datetime.now()}: Старт парсинга')

    # Настройки для запуска Chrome в headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    # Устанавливаем пользовательский агент
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 ' \
                 'YaBrowser/23.5.2.625 Yowser/2.5 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')

    service = webdriver.chrome.service.Service()

    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://sbermegamarket.ru/catalog/sushilnye-mashiny/#?filters=%7B%224CB2C27EAAFC4EB39378C4B7487E6C9E%22%3A" \
          "%5B%221%22%5D%2C%222B0B1FF4756D49CF84B094522D57ED3D%22%3A%5B%22Haier%22%5D%7D"

    driver.get(url)

    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

    # Определяем текущую дату и время (без минут)
    now = dt.datetime.now().replace(minute=0, second=0, microsecond=0)

    # Проверка директории на существование
    if not os.path.exists('./data'):
        os.makedirs('./data')

    with open(f'./data/{now.strftime("%Y_%m_%d_%H")}_index.html', "w", encoding="utf-8") as file:
        file.write(html)

    with open(f'./data/{now.strftime("%Y_%m_%d_%H")}_index.html', "r", encoding="utf-8") as file:
        html = file.read()

    soup = BeautifulSoup(html, 'lxml')

    catalogs = soup.find('div', class_='catalog-listing__items catalog-listing__items_divider')

    # Получить список всех дочерних элементов div
    elements = catalogs.find_all('div', recursive=False)

    element_list = []

    # Пройтись по каждому дочернему элементу и получить его атрибуты и содержимое
    for element in elements:
        id_product = element.find("div", class_="item-title").find("a").get("data-product-id")
        title = element.find("div", class_="item-title").find("a").get("title")
        website = "https://sbermegamarket.ru" + element.find("div", class_="item-title").find("a").get("href")
        price = element.find("div", class_="item-price").find("span").text
        price = ''.join(filter(str.isdigit, price))
        bonus_amount = element.find("span", class_="bonus-amount").text

        element_list.append(
            {
                "ИД:": id_product,
                "Наименование:": title,
                "Веб-сайт:": website,
                "Цена:": price,
                "Количество бонусов:": bonus_amount
            }
        )
    # Запись в файл json
    with open(f'./data/{now.strftime("%Y_%m_%d_%H")}_list.json', "w", encoding="utf-8") as file:
        json.dump(element_list, file, indent=4, ensure_ascii=False)

    logging.info(f'{dt.datetime.now()}: Завершение парсинга')

    os.remove(f'./data/{now.strftime("%Y_%m_%d_%H")}_index.html')


def main():
    """Задаем расписание и выполнение парсинга"""

    # Проверка директории на существование
    if not os.path.exists('./logs'):
        os.makedirs('./logs')

    # Настройка логгера
    logging.basicConfig(filename='./logs/myapp.log', level=logging.INFO, encoding='utf-8')

    logging.info(f'{dt.datetime.now()}: Запуск приложения')

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
