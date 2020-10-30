from telethon import TelegramClient, events, Button
import logging
import psycopg2

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
    [Button.inline('Образование и саморазвитие', b'edu')],
    [Button.inline('Искусство и мода', b'art')],
    [Button.inline('Спорт', b'sport')],
    [Button.inline('Закрыть кнопки', b'close')]
]


def delete_equal_posts(probability_sim=0.5):
    index_save = search_equal_posts(probability_sim)
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    for i in range(len(index_save)):
        cur.execute('DELETE from LASTPOST2 where postid = %s', (index_save[i][0]))


def search_equal_posts(probability_sim):
    from cos_sim import canonize
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT postid,channel,id,post,date from LASTPOST2")
    rows = cur.fetchall()
    con.commit()
    con.close()
    id = []
    source = []
    for row in rows:
        source.append(row[3])
        id.append(row[0])
    for i in range(len(source)):
        source[i] = canonize(source[i])
    vectorizer = CountVectorizer().fit_transform(source)
    vectors = vectorizer.toarray()
    csim = cosine_similarity(vectors)
    """Получили матрицу косинусного сходства каждого документа с каждым:
     значение a[i][j] соответсвует вероятности сходства документа i с документом j"""
    index_same = []

    for i in range(len(csim[0])):
        for j in range(i + 1, len(csim[0])):
            if csim[i][j] > probability_sim:
                index_same.append([i, j])
    for i in range(len(index_same)):
        index_same[i][0] = id[index_same[i][0]]
        index_same[i][1] = id[index_same[i][1]]

    # for i in range(len(index_same)):
        # print((rows[index_same[i][0]][3], rows[index_same[i][1]][3]), '\n')

    return index_same


def predict_category():
    from Bayes import classifyone
    model = '\\Users\\Zeden\\Desktop\\model_filefinal'
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('SELECT post from POSTDATA')
    rows = cur.fetchall
    for row in rows:
        text = row[0]
        cat = classifyone(text, model)
        cur.execute("UPDATE POSTDATA SET category = %s WHERE post = %s", (cat, text))
    con.commit()
    con.close()


def send_posts():
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT USERID from USERCHOICE")
    users = cur.fetchall
    cur.execute('SELECT * from POSTDATA')
    messages = cur.fetchall

    for user in users:
        user_choice = get_user_choice(user[0])
        for message in messages:
            cat = message[4]
            if user_choice[cat]:
                from_peer = await bot.get_input_entity(message[0])
                await bot.forward_messages(user[0], message[1], from_peer)
    con.commit()
    con.close()


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
        cur.execute("SELECT id,name,count_subs from TGDATAEXTRA")
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
    # cur.execute('SELECT * FROM USERCHOICE WHERE USERID = %s' % (sender, ))
    cur.execute("SELECT USERID,POLITICS,TECH,BUSINESS,EDUCATION,ART,SPORT from USERCHOICE")
    u_choice = {}
    for row in cur:
        if row[0] == sender:
            u_choice['politics'] = row[1]
            u_choice['tech'] = row[2]
            u_choice['business'] = row[3]
            u_choice['education'] = row[4]
            u_choice['art'] = row[5]
            u_choice['sport'] = row[6]
    con.commit()
    con.close()
    return u_choice


def is_user_new(sender):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT userid from USERCHOICE")
    rows = cur.fetchall()
    flag = False
    for row in rows:
        if str(sender) == row[0]:
            flag = True
    con.commit()
    con.close()
    return flag


def create_new_user(sender, u_choice):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    insert = "INSERT INTO USERCHOICE (USERID,POLITICS,TECH,BUSINESS,EDUCATION,ART,SPORT) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(insert, (str(sender), u_choice['politics'], u_choice['tech'], u_choice['business'],
                         u_choice['education'], u_choice['art'], u_choice['sport']))
    con.commit()
    con.close()


def on():
    from datetime import datetime
    from data_parser import parse2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT date from LASTDATE3")
    last_on = int(cur.fetchall()[0])
    if datetime.today().day - last_on > 0:
        cur.execute('TRUNCATE LASTPOST2')
        ch = get_channels()
        parse2(ch, 180, sleep_time=10, update_date=True)
        delete_equal_posts()
        predict_category()
        send_posts()
        cur.execute('UPDATE LASTDATE3 SET date = %s WHERE date = %s', (datetime.today().day, str(last_on)))
    con.commit()
    con.close()


@bot.on(events.CallbackQuery)
async def handler(event):

    u_choice = {
        'politics': 0,
        'tech': 0,
        'business': 0,
        'education': 0,
        'art': 0,
        'sport': 0
    }

    if event.data == b'polit':
        await event.answer('Успешно!')
        u_choice['politics'] = 1
    if event.data == b'tech':
        await event.answer('Хороший выбор!')
        u_choice['tech'] = 1
    if event.data == b'business':
        await event.answer('Вау!')
        u_choice['business'] = 1
    if event.data == b'edu':
        await event.answer('!')
        u_choice['education'] = 1
    if event.data == b'art':
        await event.answer('Успешно!')
        u_choice['art'] = 1
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
            on()

    else:
        await bot.send_message(sender, 'Напиши: /start')


bot.start()
bot.run_until_disconnected()
