import telebot
from telebot import types

API_TOKEN = "6303995867:AAH8Bq5pfu7RDW8YZ5Y7DJg0DwgiruClu0A"

bot = telebot.TeleBot(API_TOKEN)


class TeleBot:
    def __init__(self):
        self.links = {}

    def main_menu(self, message):
        """Метод, формирующий главное меню с кнопками "Начать парсинг", "Остановить парсинг" и "Информация"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Начать парсинг", "Остановить парсинг")
        markup.add("Информация")
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
    telebot_instance.main_menu(message)


@bot.message_handler(func=lambda message: message.text in ["Начать парсинг", "Остановить парсинг", "Информация"])
def handle_main_menu(message):
    """Обработчик сообщений из главного меню, который в зависимости от выбора пользователя вызывает соответствующий
    метод"""
    if message.text == "Начать парсинг":
        telebot_instance.store_menu(message)
    elif message.text == "Остановить парсинг":
        bot.send_message(message.chat.id, "Рассылка остановилась")
        bot.stop_polling()
    else:
        bot.send_message(message.chat.id, "Бот делает рассылку по изменению цен на выбранный товар")


@bot.message_handler(func=lambda message: message.text in ["Я.Маркет", "Озон", "Сбермегамаркет", "Назад"])
def handle_store_menu(message):
    """Обработчик сообщений из меню выбора магазина, который вызывает метод process_link_step для запроса ссылки на
    товар"""
    if message.text == "Назад":
        telebot_instance.main_menu(message)
    else:
        telebot_instance.link_menu(message)
        bot.register_next_step_handler(message, process_link_step)


def process_link_step(message):
    """Метод, который запрашивает у пользователя ссылку на товар"""
    if message.text == "Назад":
        telebot_instance.store_menu(message)
    else:
        link = message.text
        telebot_instance.confirm_menu(message, link)
        bot.register_next_step_handler(message, process_confirmation_step, link)


def process_confirmation_step(message, link):
    """Метод, который обрабатывает выбор пользователя в меню подтверждения ссылки"""
    if message.text == "Да":
        telebot_instance.links[message.chat.id] = link
        bot.send_message(message.chat.id, "Ссылка сохранена")
        telebot_instance.main_menu(message)
    elif message.text == "Нет":
        bot.send_message(message.chat.id, "Пришлите ссылку на товар")
        bot.register_next_step_handler(message, process_link_step)
    elif message.text == "Назад":
        telebot_instance.store_menu(message)
    else:
        bot.send_message(message.chat.id, "Выберите 'Да' или 'Нет'")
        telebot_instance.confirm_menu(message, link)
        bot.register_next_step_handler(message, process_confirmation_step, link)


bot.polling()
