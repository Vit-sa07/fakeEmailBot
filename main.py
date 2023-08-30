import telebot
import random
import string
import time
import os
import requests

API = 'https://www.1secmail.com/api/v1/'
domain_list = ["1secmail.com", "1secmail.org", "1secmail.net"]

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # Замените на ваш реальный токен бота
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать во временный почтовый бот! Пришлите мне любое сообщение, чтобы начать.")


def generate_username():
    name = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(name) for i in range(10))
    return username


def check_mail(mail='', chat_id=None):
    req_link = f'{API}?action=getMessages&login={mail.split("@")[0]}&domain={mail.split("@")[1]}'
    r = requests.get(req_link).json()
    length = len(r)

    if length == 0:
        bot.send_message(chat_id, '[INFO] В почтовом ящике нет новых сообщений. Проверка каждые 5 секунд!')
    else:
        id_list = []

        for i in r:
            for k, v in i.items():
                if k == 'id':
                    id_list.append(v)

        bot.send_message(chat_id, f'[+] У вас {length} новые входящие сообщения! Почтовый ящик обновляется каждые 5 секунд!')

        current_dir = os.getcwd()
        final_dir = os.path.join(current_dir, 'all_mails')

        if not os.path.exists(final_dir):
            os.makedirs(final_dir)

        for i in id_list:
            read_msg = f'{API}?action=readMessage&login={mail.split("@")[0]}&domain={mail.split("@")[1]}&id={i}'
            r = requests.get(read_msg).json()

            sender = r.get('from')
            subject = r.get('subject')
            date = r.get('date')
            content = r.get('textBody')

            mail_info = f'Sender: {sender}\nTo: {mail}\nSubject: {subject}\nDate: {date}\nContent: {content}'
            bot.send_message(chat_id, mail_info)


def delete_mail(mail='', chat_id=None):
    url = 'https://www.1secmail.com/mailbox'

    data = {
        'action': 'deleteMailbox',
        'login': mail.split('@')[0],
        'domain': mail.split('@')[1]
    }

    r = requests.post(url, data=data)
    bot.send_message(chat_id, f'[X] Email  {mail} - удален!\n')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        username = generate_username()
        mail = f'{username}@{random.choice(domain_list)}'
        bot.send_message(message.chat.id, f'[+] Ваш временный адрес электронной почты: {mail}')

        while True:
            check_mail(mail=mail, chat_id=message.chat.id)
            time.sleep(5)

    except KeyboardInterrupt:
        delete_mail(mail=mail, chat_id=message.chat.id)
        bot.send_message(message.chat.id, 'Программа прервана!')


if __name__ == '__main__':
    bot.polling()
