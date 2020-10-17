from telethon import TelegramClient, events, Button
import logging

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

api_id = ''
api_hash = ''
bot_token = ''

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
def PredictPostsCat():
    from test_evaluate import test_and_evaluate
    pass

def SelectPostsToThereDB():
    pass
def SendPosts():
    pass

def get_user_choice(sender):
    pass

def IsUserNew(sender):
    import psycopg2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT channel,id,post,date from LASTPOST1")
    rows = cur.fetchall()
    flag = False
    for row in rows:
        if sender == row[0]:
            flag = True
    con.commit()
    con.close()
    return flag


def CreateNewUser(sender):
    import psycopg2
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    postgres_insert_query = """INSERT INTO USERCHOICE (USERID, POLITICS, TECH, BUSINESS, EDUCATION, ART, SPORT) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cur.execute(postgres_insert_query, (sender, u_choice['politics'], u_choice['tech'], u_choice['business'], u_choice['education'],
                                        u_choice['art'], u_choice['sport']))
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
    if not IsUserNew(sender):
        await bot.send_message(sender, "Выберете категории:", buttons=buttons)
        CreateNewUser(sender)

    if '/start' or '/help' in event.raw_text:
        await bot.send_message(sender, 'Привет')

    else:

        from_peer = await bot.get_input_entity('bitkogan')
        await bot.forward_messages(sender, 8717, from_peer)


bot.start()
bot.run_until_disconnected()
