import constants
import telebot
import pymysql as db
import datetime
import time

# объявляем бота
bot = telebot.TeleBot(constants.token)
bot.config['api_key'] = constants.token
# конект и курсор к БД
conn = db.connect(host=constants.host, port=constants.port, user=constants.user, passwd=constants.password)
cursor = conn.cursor()

users = set()  # сет, хранящий текущий список пользователей для рассылки
pendings = []  # список ответов с пендингом, обнуляется каждые <constants.interval> секунд

# запрашиваем обновления бота, редактируем список пользователей
updates = bot.get_updates()['result']
for upd in updates:
    if upd['message']['text'] == '/start':
        users.add(upd['message']['from']['id'])
    if upd['message']['text'] == '/stop' or upd['message']['text'] == '/end':
        if users.__contains__(upd['message']['from']['id']):
            users.remove(upd['message']['from']['id'])

# основной цикл
while True:
    # рассылаем собранные пендинги и обнуляем список пендингов
    if len(pendings) != 0:
        for user in users:
            bot.send_message(user, ' '.join(pendings))
    pendings = []
    # выполняем SQL - скрипт
    cursor.execute(constants.sql)
    # обрабатываем ответ БД
    for fetched in cursor.fetchall():
        # проверка на актуальность записи
        if (datetime.datetime.now() - fetched[1]).seconds > constants.interval:
            break
        # если статус ServerError
        if fetched[-1] == 'ServerError':
            text = 'ServerError: id ' + fetched[0].__str__()
            for user in users:
                bot.send_message(user, text)
        # если статус Pending
        elif fetched[-1] == "Pending":
            pendings.append('Pending: id ' + fetched[0].__str__() + ' ' + fetched[1].__str__())
    # проверяем последний апдейт бота
    upd = bot.get_updates()['result'][-1]
    if upd['message']['text'] == '/start':
        users.add(upd['message']['from']['id'])
    if upd['message']['text'] == '/stop' or upd['message']['text'] == '/end':
        if users.__contains__(upd['message']['from']['id']):
            users.remove(upd['message']['from']['id'])
    # ожидание в <constants.interval> секунд
    time.sleep(constants.interval)



