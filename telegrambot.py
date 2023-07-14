import json
import telebot
import parse_helpers
from telebot import types


API_TOKEN = "6303995867:AAH8Bq5pfu7RDW8YZ5Y7DJg0DwgiruClu0A"

bot = telebot.TeleBot(API_TOKEN)
is_bot_running = False

class TeleBot:
    def __init__(self):
        self.links = {}

    def main_menu(self, message):
        """Метод, формирующий главное меню с кнопками "Начать парсинг", "Остановить парсинг" и "Информация"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Начать парсинг", "Остановить парсинг")
        markup.add("Информация", "Вывести все ссылки")
        markup.add("Скрыть меню")
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

    def store_menu(self, message):
        """Метод, формирующий меню выбора магазина с кнопками "Я.Маркет", "Озон" и "Сбермегамаркет"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Я.Маркет", "Озон", "Сбермегамаркет")
        markup.add("Назад")
        bot.send_message(message.chat.id, "Выберите магазин:", reply_markup=markup)

    def confirm_menu(self, message, link):
        """Метод, формирующий меню подтверждения введенной ссылки с кнопками "Да" и "Нет"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Да", "Нет")
        markup.add("Назад")
        bot.send_message(
            message.chat.id,
            f"Вы ввели ссылку: {link}, верно?",
            reply_markup=markup,
        )

    def link_menu(self, message):
        """Метод, формирующий меню запроса ссылки с кнопкой Назад"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Назад")
        bot.send_message(
            message.chat.id,
            "Пришлите ссылку на товар",
            reply_markup=markup,
        )


# Создание экземпляра класса TeleBot
telebot_instance = TeleBot()


@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработчик команды /start, который вызывает метод main_menu при запуске бота"""
    global is_bot_running
    if not is_bot_running:
        telebot_instance.main_menu(message)
        is_bot_running = True
    else:
        bot.send_message(message.chat.id, "Бот уже запущен!")
        telebot_instance.main_menu(message)

@bot.message_handler(commands=['stop'])    
def handle_stop(message):
    """Обработчик команды /stop, который будет останавливать парсинга сайта"""
    global is_bot_running  
    if is_bot_running:
        bot.send_message(message.chat.id, "Бот остановлен! Для старта бота введите '/start'", reply_markup=types.ReplyKeyboardRemove())
        is_bot_running = False
    else:
        bot.send_message(message.chat.id, "Бот уже остановлен!")

@bot.message_handler(commands=['menu'])    
def handle_menu(message):
    """Обработчик команды /menu, который отображает главное меню"""
    telebot_instance.store_menu(message)


@bot.message_handler(func=lambda message: message.text in ["Начать парсинг", "Остановить парсинг", "Информация", "Вывести все ссылки", "Скрыть меню"])
def handle_main_menu(message):
    """Обработчик сообщений из главного меню, который в зависимости от выбора пользователя вызывает соответствующий
    метод"""
    if message.text == "Начать парсинг":
        telebot_instance.store_menu(message)
    elif message.text == "Остановить парсинг":
        bot.send_message(message.chat.id, "Рассылка остановилась")
        handle_stop(message)
    elif message.text == "Вывести все ссылки":
        if telebot_instance.links:
            result = ''
            for item in telebot_instance.links[message.chat.id]:
                market = item['market']
                link = item['link']
                result += f'<u>{market}</u>: {link}\n'
            bot.send_message(message.chat.id, result, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Список ссылок к парсингу пустой!")
    elif message.text == "Скрыть меню":
        bot.send_message(message.chat.id, text="Клавиатура скрыта. Для отображения клавиатуры введите команду /menu", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Бот делает рассылку по изменению цен на выбранный товар")


@bot.message_handler(func=lambda message: message.text in ["Я.Маркет", "Озон", "Сбермегамаркет", "Назад"])
def handle_store_menu(message):
    """Обработчик сообщений из меню выбора магазина, который вызывает метод process_link_step для запроса ссылки на
    товар"""
    if message.text == "Назад":
        telebot_instance.main_menu(message)
    else:
        market = message.text
        telebot_instance.link_menu(message)
        bot.register_next_step_handler(message, process_link_step, market)


def process_link_step(message, market):
    """Метод, который запрашивает у пользователя ссылку на товар"""
    if message.text == "Назад":
        telebot_instance.store_menu(message)
    else:
        link = message.text
        telebot_instance.confirm_menu(message, link)
        bot.register_next_step_handler(message, process_confirmation_step, link, market)


def process_confirmation_step(message, link, market):
    """Метод, который обрабатывает выбор пользователя в меню подтверждения ссылки"""
    if message.text == "Да":
        if parse_helpers.check_link(link):
            # Для нового chat_id - пустой список
            if message.chat.id not in telebot_instance.links:
                telebot_instance.links[message.chat.id] = []
            # Добавляем новую запись в список для данного chat_id  
            telebot_instance.links[message.chat.id].append({
                'market': market,
                'link': link
            })
            # Запись в файл json
            with open(f'./data/turn_list.json', "w", encoding="utf-8") as file:
                json.dump(telebot_instance.links, file, indent=4, ensure_ascii=False)
            bot.send_message(message.chat.id, "Ссылка сохранена")
            telebot_instance.main_menu(message)
        else:
            bot.send_message(message.chat.id, "Неккоректный адрес. Пришлите ссылку на товар повторно!")
            bot.register_next_step_handler(message, process_link_step)
    elif message.text == "Нет":
        bot.send_message(message.chat.id, "Пришлите ссылку на товар")
        bot.register_next_step_handler(message, process_link_step)
    elif message.text == "Назад":
        telebot_instance.store_menu(message)
    else:
        bot.send_message(message.chat.id, "Выберите 'Да' или 'Нет'")
        telebot_instance.confirm_menu(message, link)
        bot.register_next_step_handler(message, process_confirmation_step, link)