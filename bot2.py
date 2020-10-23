from telethon import TelegramClient, events, Button
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

api_id = 1999880
api_hash = '0e8b4dc0b4c5fc7ef1d90471f9023e7d'
bot_token = '1340604025:AAGg4aJWBuphR_71n1ingr6LoUj1j-VtvHM'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
buttons = [
    [Button.inline('Экономика и бизнес', b'economy')],
    [Button.inline('Политика', b'polit')],
    [Button.inline('Технологии и наука', b'tech')],
    [Button.inline('Образование и саморазвитие', b'edu')],
    [Button.inline('Искусство и мода', b'art')],
    [Button.inline('Спорт', b'sport')]
]

u_choice = {
    'politics': 0,
    'tech': 0,
    'business': 0,
    'education': 0,
    'art': 0,
    'sport': 0
}


def get_to_database():
    import psycopg2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    return cur

def shingle_posts():
    pass


def predict_category(text):
    from Bayes import classifyone
    model = '\\Users\\Zeden\\Desktop\\model_filefinal'
    return classifyone(text, model)


def select_posts_to_db():
    pass


def send_posts():
    pass


def get_channels(amount_top, amount_bottom):
    from datetime import datetime
    now = datetime.today().day
    import psycopg2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT date,num_bottom from LASTDATE1")
    rows = cur.fetchall()
    num_of_bottom = rows[0][1]
    if num_of_bottom == 16:
        num_of_bottom = 1
    cur.execute("""TRUNCATE LASTDATE1""")
    if rows[0][0] != now:
        insert = "INSERT INTO LASTDATE1 (DATE,NUM_BOTTOM) VALUES (%s,%s)"
        cur.execute(insert, (now, num_of_bottom+1))
        return sort_channels(amount_top, amount_bottom,)
    con.commit()
    con.close()


def sort_channels(amount_top, amount_bottom, number_of_bottom):
    import psycopg2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT id,name,count_subs from TGDATAEXTRA")
    rows = cur.fetchall()
    rows = sorted(rows, key=lambda subs: subs[2], reverse=True)
    ch_top = []
    ch_bottom = []

    for i in range(len(rows)):
        border1 = amount_top + amount_bottom * (number_of_bottom - 1)
        border2 = amount_top + amount_bottom * number_of_bottom
        if border2 > len(rows) - 1:
            border2 = len(rows) - 1
        if border1 <= i < border2:
            ch_bottom.append(rows[i][1])
        if i < amount_top:
            ch_top.append(rows[i][1])

    con.commit()
    con.close()
    return ch_top, ch_bottom

def get_user_choice(sender):
    import psycopg2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute('''SELECT * FROM USERCHOICE WHERE userid, = %s''', (sender,))
    for row in cur:
        u_choice['politics'] = row[1]
        u_choice['tech'] = row[2]
        u_choice['business'] = row[3]
        u_choice['education'] = row[4]
        u_choice['art'] = row[5]
        u_choice['sport'] = row[6]
    con.commit()
    con.close()


def is_user_new(sender):
    import psycopg2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT userid from USERCHOICE")
    rows = cur.fetchall()
    flag = False
    for row in rows:
        if sender == row[0]:
            flag = True
    con.commit()
    con.close()
    return flag


def create_new_user(sender):
    import psycopg2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    insert = "INSERT INTO USERCHOICE (USERID,POLITICS,TECH,BUSINESS,EDUCATION,ART,SPORT) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(insert, (sender, u_choice['politics'], u_choice['tech'], u_choice['business'],
                         u_choice['education'], u_choice['art'], u_choice['sport']))
    con.commit()
    con.close()


@bot.on(events.CallbackQuery)
async def handler(event):
    if event.data == b'polit':
        await event.answer('Успешно')
        u_choice['politics'] = 1
    if event.data == b'tech':
        await event.answer('Успешно')
        u_choice['tech'] = 1
    if event.data == b'business':
        await event.answer('Успешно')
        u_choice['business'] = 1
    if event.data == b'edu':
        await event.answer('Успешно')
        u_choice['education'] = 1
    if event.data == b'art':
        await event.answer('Успешно')
        u_choice['art'] = 1
    if event.data == b'sport':
        await event.answer('Успешно')
        u_choice['sport'] = 1


@bot.on(events.NewMessage)
async def meh(event):
    sender = await event.get_sender()
    if not is_user_new(sender):
        await bot.send_message(sender, "Выберете категории:", buttons=buttons)
        create_new_user(sender)
    else:
        get_user_choice(sender)

    if '/start' or '/help' in event.raw_text:
        await bot.send_message(sender, 'Привет')

    else:

        from_peer = await bot.get_input_entity('bitkogan')
        await bot.forward_messages(sender, 8717, from_peer)


bot.start()
bot.run_until_disconnected()
