import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Настройки для запуска Chrome в headless mode
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

# Устанавливаем пользовательский агент
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.2.625 Yowser/2.5 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(options=chrome_options)

url = "https://sbermegamarket.ru/catalog/sushilnye-mashiny/#?filters=%7B%224CB2C27EAAFC4EB39378C4B7487E6C9E%22%3A%5B%221%22%5D%2C%222B0B1FF4756D49CF84B094522D57ED3D%22%3A%5B%22Haier%22%5D%7D"

driver.get(url)

html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

# html = driver.page_source

with open("./SberParsing/index.html", "w", encoding='utf-8') as file:
    file.write(html)

with open("./SberParsing/index.html", "r", encoding='utf-8') as file:
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
     bonus_amount = element.find("span", class_="bonus-amount").text
     element_list.append(
          {
               "ИД:": id,
               "Наименование:": title,
               "Веб-сайт:": website,
               "Цена:": price,
               "Количество бонусов:": bonus_amount
          }
     )


with open("./SberParsing/list.json", "a", encoding='utf-8') as file:
     json.dump(element_list, file, indent=4, ensure_ascii=False)

