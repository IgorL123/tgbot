from telethon import TelegramClient, events, Button
import logging
import psycopg2
import telethon
import time
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import datetime
from Bayes import NaiveBayesModel

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

api_id = 1999880
api_hash = '0e8b4dc0b4c5fc7ef1d90471f9023e7d'
bot_token = '1340604025:AAGg4aJWBuphR_71n1ingr6LoUj1j-VtvHM'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
buttons = [
    [Button.inline('Экономика и бизнес', b'business')],
    [Button.inline('Политика', b'polit')],
    [Button.inline('Технологии и наука', b'tech')],
    [Button.inline('Развлечение', b'ent')],
    [Button.inline('Спорт', b'sport')],
    [Button.inline('Закрыть кнопки', b'close')]
]


def delete_equal_posts(probability_sim=0.4):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    from cos_sim import canonize
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    cur.execute("SELECT postid,post,id from LASTPOST5")
    rows = cur.fetchall()
    for i in range(len(rows)):
        cur.execute("UPDATE LASTPOST5 SET postid = %s WHERE id = %s", (i, rows[i][2]))
    id = []
    source = []
    for row in rows:
        source.append(canonize(row[1]))
        id.append(row[0])
    vectorizer = CountVectorizer().fit_transform(source)
    vectors = vectorizer.toarray()
    csim = cosine_similarity(vectors)
    """Получили матрицу косинусного сходства каждого документа с каждым:
     значение a[i][j] соответсвует вероятности сходства документа i с документом j"""

    for i in range(len(csim[0])):
        for j in range(i + 1, len(csim[0])):
            if csim[i][j] > probability_sim:
                cur.execute('DELETE from LASTPOST5 where postid = %s', (i,))

    con.commit()
    con.close()


def predict_category():
    from Bayes import classify_one
    model = '\\Users\\Zeden\\Desktop\\model_filefinal'
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('SELECT post from LASTPOST5')
    rows = cur.fetchall()
    for row in rows:
        text = row[0]
        cat = classify_one(text, model)
        cur.execute("UPDATE LASTPOST5 SET category = %s WHERE post = %s", (cat, text))
    con.commit()
    con.close()


async def send_posts(time_to_sleep=2):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT USERID from USERCHOICE2")
    users = cur.fetchall()
    cur.execute('SELECT * from LASTPOST5')
    messages = cur.fetchall()
    con.commit()
    con.close()

    for user in users:
        if int(user[0]) == 428335967:
            continue
        user_choice = get_user_choice(user[0])
        for message in messages:
            cat = message[4]
            if user_choice[cat]:
                try:
                    from_peer = await bot.get_input_entity(str(message[2]))
                    time.sleep(time_to_sleep)
                    await bot.forward_messages(int(user[0]), message[1], from_peer,silent=True)
                except (telethon.errors.rpcerrorlist.MessageIdInvalidError,
                        telethon.errors.rpcerrorlist.UserIsBlockedError):
                    continue


def get_channels(amount_top=150, amount_bottom=30):
    from datetime import datetime
    now = datetime.today().day
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT date,num_bottom from LASTDATE1")
    rows = cur.fetchall()
    num_of_bottom = 0 if rows[0][1] == (630 - amount_top) // amount_bottom else rows[0][1]
    if rows[0][0] != now:
        cur.execute("UPDATE LASTDATE1 SET date = %s, num_bottom = %s WHERE date = %s",
                    (now, num_of_bottom+1, rows[0][0]))
        cur.execute("SELECT id,name,count_subs from TGCHANNELS2")
        rows = cur.fetchall()
        con.commit()
        con.close()
        rows = sorted(rows, key=lambda subs: subs[2], reverse=True)
        ch_top = []
        ch_bottom = []

        for i in range(len(rows)):
            border1 = amount_top + amount_bottom * num_of_bottom
            border2 = amount_top + amount_bottom * (num_of_bottom + 1)
            if border2 > len(rows) - 1:
                border2 = len(rows) - 1
            if border1 <= i < border2:
                ch_bottom.append(rows[i][1])
            if i < amount_top:
                ch_top.append(rows[i][1])

        return ch_top + ch_bottom


def get_user_choice(sender):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    sender = str(sender)
    cur.execute('SELECT * FROM USERCHOICE2 WHERE USERID = %s', (sender, ))
    u_choice = {}
    for row in cur:
        if row[0] == sender:
            u_choice['politics'] = row[1]
            u_choice['tech'] = row[2]
            u_choice['business'] = row[3]
            u_choice['entertainment'] = row[4]
            u_choice['sport'] = row[5]
    con.commit()
    con.close()
    return u_choice


def is_user_new(sender):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('SELECT USERID from USERCHOICE2 WHERE USERID = %s', (str(sender),))
    rows = cur.fetchall()
    con.commit()
    con.close()
    if len(rows) > 0:
        return True
    else:
        return False


def create_new_user(sender, u_choice):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    insert = "INSERT INTO USERCHOICE2 (USERID,POLITICS,TECH,BUSINESS,ENTERTAINMENT,SPORT) VALUES (%s,%s,%s,%s,%s,%s)"
    cur.execute(insert, (str(sender), u_choice['politics'], u_choice['tech'], u_choice['business'],
                         u_choice['entertainment'], u_choice['sport']))
    con.commit()
    con.close()


def parse_channels(channels, amount_to_parse=180, sleep_period=49, sleep_time=120, update_id=True):
    ''' Ограничение примерно в 500 тг каналов '''
    if channels is None:
        print('None')
        return 0
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    for i in range(min(amount_to_parse, len(channels))):
        #print(i, ' ', channels[i])
        if i % sleep_period == 0 and i != 0:
            time.sleep(sleep_time)
        cur.execute('SELECT name,last_id from TGCHANNELS2 WHERE name = %s', (channels[i],))
        row = cur.fetchall()
        new_id = last_id = row[0][1]
        limit_to_parse = 100
        if last_id == 0:
            limit_to_parse = 1
        try:
            channel_entity = bot.get_input_entity(channels[i])
            post = bot(GetHistoryRequest(
                peer=channel_entity,
                limit=limit_to_parse,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=last_id,
                add_offset=0,
                hash=0))
            messages = post.messages
            last_message = []
            for message in messages:
                last_message.append(message.to_dict())

            for j in range(len(last_message)):
                jsnfile = last_message[j]
                if jsnfile['message'] == '':
                    break
                insert = """INSERT INTO LASTPOST5 (POSTID,CHANNEL,ID,POST) VALUES (%s,%s,%s,%s)"""
                to_insert = (0, channels[i], jsnfile['id'], jsnfile['message'])
                cur.execute(insert, to_insert)
                new_id = jsnfile['id']

            if update_id:
                cur.execute('UPDATE TGCHANNELS2 SET last_id = %s WHERE name = %s', (int(new_id), channels[i],))

            con.commit()

        except (ValueError, KeyError, telethon.errors.rpcerrorlist.UsernameNotOccupiedError, TypeError,
                telethon.errors.rpcerrorlist.ChannelPrivateError, telethon.errors.rpcerrorlist.UsernameInvalidError):
            pass
    con.close()


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
        create_new_user(sender.id, u_choice=u_choice)
        await bot.send_message(sender, 'Категории выбраны!', buttons=Button.clear())


@bot.on(events.NewMessage)
async def meh(event):
    sender = await event.get_sender()
    if '/start' in event.raw_text:
        await bot.send_message(sender, 'Привет')
        if not is_user_new(sender.id):
            await bot.send_message(sender, "Выберете категории:", buttons=buttons)
        else:

            con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1",
                                   port="5433")
            cur = con.cursor()
            cur.execute("SELECT date from LASTDATE3")
            last_on = int(cur.fetchall()[0][0])
            if datetime.today().day - last_on > 0 or True:
                #cur.execute('TRUNCATE LASTPOST2')
                #cur.execute('UPDATE LASTDATE2 SET date = %s WHERE date = %s', (datetime.today().day, str(last_on)))
                con.commit()
                con.close()
                '''
                ch = get_channels()
                parse_channels(ch, 200, sleep_time=10, update_id=True)
                delete_equal_posts()
                predict_category()
                '''

                await send_posts()

                '''
                from_peer = await bot.get_input_entity('belamova')
                user = 428335967
                await bot.forward_messages(user, 11819, from_peer)
                '''
    else:
        await bot.send_message(sender, 'Напиши: /start')


bot.start()
bot.run_until_disconnected()
