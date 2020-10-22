import psycopg2
import time
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

api_id = 1999880
api_hash = "0e8b4dc0b4c5fc7ef1d90471f9023e7d"
username = 'redneck88'

client = TelegramClient(username, api_id, api_hash)
client.start()

def get_tg_channels():
    channel = []
    con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="abcd0987",
        host="127.0.0.1",
        port="5433")
    cur = con.cursor()
    cur.execute("SELECT name from TGDATAFULL")
    rows = cur.fetchall()
    for row in rows:
        channel.append(row[0])
    con.commit()
    con.close()
    return channel


def save_data_in_db(message, dates, Messageid, channel_name):
    con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="abcd0987",
        host="127.0.0.1",
        port="5433")
    cur = con.cursor()
    postgres_insert_query = """INSERT INTO LASTPOST1 (CHANNEL,ID,POST,DATE) VALUES (%s,%s,%s,%s)"""
    to_insert = (channel_name, Messageid, message, dates)
    cur.execute(postgres_insert_query, to_insert)
    con.commit()
    con.close()


def get_last_post(channel_username):
    channel_entity = client.get_input_entity(channel_username)
    while True:
        post = client(GetHistoryRequest(
            peer=channel_entity,
            limit=1,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0))
        if not post.messages:
            break
        messages = post.messages
        last_message = []
        for message in messages:
            last_message.append(message.to_dict())
        jsnfile = last_message[0]
        save_data_in_db(jsnfile['message'], jsnfile['date'], jsnfile['id'], channel_username)
        break


ch_nm = get_tg_channels()
count = 0
for i in range(len(ch_nm)):
    try:
        get_last_post(ch_nm[i])
        count += 1
        print(i)
        if count == 49:
            time.sleep(120)
            count = 0
    except ValueError:
        continue
    except KeyError:
        continue

