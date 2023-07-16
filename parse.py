import datetime as dt
import json
import os
import time

import schedule
import parse_helpers

from bs4 import BeautifulSoup
from telegrambot import bot

def parse_sber(url):
     """Функция, для парсинга сайта sbermegamarket"""
     driver = parse_helpers.get_settings_driver()
     # Переходим по ссылке
     driver.get(url)
     # Выполняем js на сайте и сохраняем html страницу
     html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
     # Закрывает драйвер
     driver.quit()

     # Начинаем парсить html страничку
     soup = BeautifulSoup(html, 'lxml')
     
     product_id = url[url.rfind('-') + 1:]
          
     title = soup.find("h1", class_="pdp-header__title pdp-header__title_only-title page-title").text
     # Удаляем табуляцию и переходы
     title = title.replace('\t','')
     title = title.replace('\n','')  
     
     price = soup.find("div", class_="pdp-sales-block__price-wrap pdp-sales-block__price-wrap_active").find("meta").get("content")
     bonus_amount = soup.find("div", class_="money-bonus pdp-sales-block__bonus lg money-bonus_loyalty pdp-sales-block__bonus_active").find("span", class_="bonus-amount").text

     # Сохраним полученные данные в словарь
     element_list = []
     element_list.append(
          {
               "id": product_id,
               "title": title,
               "website": url,
               "price": price,
               "bonus_amount": bonus_amount
          }
     )

     return element_list


def parse():
     """Основная функция для определения типа парсинга"""

     # Проверка директории на существование
     if not os.path.exists('./data'):
          os.makedirs('./data')

     if not os.path.exists("./data/turn_list.json"):
          return
     
     # Чтение файла json
     with open(f'./data/turn_list.json', encoding="utf-8") as file:
          turn_data = json.load(file) 
           
     for chat_id, chat_data in turn_data.items():
          
          for data in chat_data:
               
               link = data['link']
               market = data['market']

               # Убираем слеш в конце строки, если есть
               url = link.rstrip('/')
               
               # Определяем текущую дату и время (без минут)
               str_now = dt.datetime.now().replace(minute=0, second=0, microsecond=0).strftime("%Y_%m_%d_%H")

               # Получаем список с данныыми с сайта
               if market == "Сбермегамаркет":
                    element_list = parse_sber(url=url)
               else:
                    bot.send_message(chat_id, "Сейчас доступен только парсинг Сбермегамаркета. Ждите обновлений!")
               
               # Запись в файл json
               with open(f'./data/{str_now}_{market}_list.json', "w", encoding="utf-8") as file:
                    json.dump(element_list, file, indent=4, ensure_ascii=False)
               
               # Находим расхождения с предыдущим файлом
               diff = parse_helpers.compare_json_files(file.name, str_now, market)
               
               # Формироуем сообщением для бота
               message = parse_helpers.generate_bot_message(diff)

               if message:
                    # Должна быть отправка сообщения боту по чатам
                    bot.send_message(chat_id, message)
                    # print(message)


def start_parse():
     
     # Задаем расписание выполнения задачи раз в час
     schedule.every().hour.do(parse)

     # Бесконечный цикл, который выполняет код каждый час
     while True:
          schedule.run_pending()
          time.sleep(60 * 30)
     

if __name__ == "__main__":
    start_parse()
