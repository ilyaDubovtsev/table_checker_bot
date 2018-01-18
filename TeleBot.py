import constants
import telebot
import pymysql as db
import datetime
import time


bot = telebot.TeleBot(constants.token)


def get_db_updates():
    conn = db.connect(host=constants.host, port=constants.port, user=constants.user, passwd=constants.password)
    cursor = conn.cursor()
    cursor.execute(constants.sql)
    return cursor.fetchall()


def file_updater(id, inter):
    new_users = []
    with open('users', 'r') as users:
        if users.read() != '':
            new_users = []
            for user in users:
                if not user.split(' ')[0] == str(id):
                    new_users.append(user)
        new_users.append('{id} {interval}'.format(id=id, interval=inter))
    with open('users', 'w') as users:
        if len(new_users) != 0:
            users.write('\n'.join(new_users))


@bot.message_handler(commands=['start'])
def start(message):
    sent = bot.send_message(message.chat.id, 'Как часто вы хотите получать оповещения (в минутах)?')
    bot.register_next_step_handler(sent, set_interval)


def set_interval(message):
    id = message.chat.id
    inter = message.text
    file_updater(id, inter)
    sent = bot.send_message(message.chat.id, 'Установлен интервал в {interval} минут.'.format(interval=message.text))
    main_loop(message)


def main_loop(message):
    id = message.chat.id
    interval_in_min = 1
    ids = []
    while True:
        pendings = []
        with open('users', 'r') as users:
            for user in users:
                str_list = user.split(' ')
                if str_list[0] == str(id):
                    interval_in_min = int(str_list[1]) * 60
        if interval_in_min < 0:
            break
        fetched = get_db_updates()
        for line in fetched:
            if line[2] == 'ServerError' and not ids.__contains__(line[0]):
                bot.send_message(id, 'ServerError: id {id}'.format(id=line[0]))
                if len(ids) >= 50:
                    ids = ids[1:]
                ids.append(line[0])
            if line[2] == 'Pending' and not ids.__contains__(line[0]) \
                    and (datetime.datetime.now() - line[1]).total_seconds() > 600:
                pendings.append('Pending: id {id} {time}'
                                .format(id=line[0], time=line[1].__str__()))
                if len(ids) >= 50:
                    ids = ids[1:]
                ids.append(line[0])
        if len(pendings) != 0:
            bot.send_message(id, '\n'.join(pendings))
        bot.send_message(id, '1')
        time.sleep(interval_in_min)


@bot.message_handler(commands=['interval'])
def interval(message):
    sent = bot.send_message(message.chat.id, 'Как часто вы хотите получать оповещения (в минутах)?')
    bot.register_next_step_handler(sent, update_interval)


def update_interval(message):
    id = message.chat.id
    inter = message.text
    file_updater(id, inter)
    bot.send_message(message.chat.id, 'Интервал изменен на {interval} минут.'.format(interval=inter))


@bot.message_handler(commands=['stop'])
def stop(message):
    id = message.chat.id
    file_updater(id, -1)
    bot.send_message(id, "Работа завершена.")


bot.polling()
