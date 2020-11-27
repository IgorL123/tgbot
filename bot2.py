from telethon import TelegramClient, events, Button
import logging
import psycopg2
import telethon
import time
from Bayes import NaiveBayesModel
from data_process import process_data
from data_parser import parse
import database
import datetime
from config import (API_ID, API_HASH, BOT_TOKEN)


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
buttons = [
    [Button.inline('Экономика и бизнес', b'business')],
    [Button.inline('Политика', b'polit')],
    [Button.inline('Технологии и наука', b'tech')],
    [Button.inline('Развлечение', b'ent')],
    [Button.inline('Спорт', b'sport')],
    [Button.inline('Закрыть кнопки', b'close')]
]
buttons_to_change = [
    [Button.inline('Да', b'yes')],
    [Button.inline('Нет', b'no')]
]


async def send_posts(time_to_sleep=10, amount_to_send=0):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT USERID from USERCHOICE2")
    users = cur.fetchall()
    cur.execute('SELECT * from DATA')
    messages = cur.fetchall()
    con.commit()
    con.close()
    amount_to_send = len(messages) if amount_to_send == 0 else amount_to_send
    for user in users:
        user_choice = database.get_user_choice(user[0])
        sended = 0
        for message in messages:
            if sended == amount_to_send:
                break
            cat = message[4]
            if user_choice[cat]:
                try:
                    from_peer = await bot.get_input_entity(str(message[2]))
                    time.sleep(time_to_sleep)
                    await bot.forward_messages(int(user[0]), message[1], from_peer, silent=True)
                    sended += 1
                except (telethon.errors.rpcerrorlist.MessageIdInvalidError,
                        telethon.errors.rpcerrorlist.UserIsBlockedError):
                    continue


u_choice = {
        'politics': 0,
        'tech': 0,
        'business': 0,
        'entertainment': 0,
        'sport': 0
    }


@bot.on(events.CallbackQuery)
async def handler(event):
    if event.data == b'polit':
        await event.answer('Успешно!')
        u_choice['politics'] = 1
    if event.data == b'tech':
        await event.answer('Хороший выбор!')
        u_choice['tech'] = 1
    if event.data == b'business':
        await event.answer('Вау!')
        u_choice['business'] = 1
    if event.data == b'ent':
        await event.answer('Успешно!')
        u_choice['entertainment'] = 1
    if event.data == b'sport':
        await event.answer('Успешно!')
        u_choice['sport'] = 1
    if event.data == b'close':
        await event.answer('Успешно')
        sender = await event.get_sender()
        database.create_new_user(sender.id, u_choice=u_choice)
        await bot.send_message(sender, 'Категории выбраны!', buttons=Button.clear())

    if event.data == b'yes':
        sender = await event.get_sender()
        database.delete_user(sender.id)
        await bot.send_message(sender, "Выбери категории:", buttons=buttons)
    if event.data == b'no':
        sender = await event.get_sender()
        await bot.send_message(sender, "Ок")


@bot.on(events.NewMessage)
async def meh(event):

    sender = await event.get_sender()
    if '/start' in event.raw_text:

        await bot.send_message(sender, 'Привет')
        if not database.is_user_new(sender.id):
            await bot.send_message(sender, "Выбери категории:", buttons=buttons)
        else:
            await bot.send_message(sender, 'Хочешь изменить выбор?', buttons=buttons_to_change)
    else:

        await bot.send_message(sender, 'Напиши: /start')
    
    f = open('last_date.txt')
    last_time = f.read()
    if abs(datetime.datetime.now().hour - int(last_time)) > 0:
        f = open('last_date.txt', 'w')
        f.write(str(datetime.datetime.now().hour))
        f.close()

        if abs(datetime.datetime.now().hour - int(last_time)) > 24:
            database.truncate_all_data()

        database.truncate_tempdata()
        ch = database.get_channels(amount_bottom=10, amount_top=390)
        await parse(ch, 400, sleep_time=10, update_id=True)

        process_data(probability_sim=0.3, rnn=True)
        await send_posts(amount_to_send=0)

    if '/help' in event.raw_text:
        pass


bot.start()
bot.run_until_disconnected()
