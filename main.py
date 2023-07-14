from parse import start_parse
from threading import Thread

from telegrambot import bot


def main():

    # Запуск бота
    bot_thread = Thread(target=bot.polling)
    bot_thread.start()

    parse_thread = Thread(target=start_parse)
    parse_thread.start()


if __name__ == '__main__':    
    main()