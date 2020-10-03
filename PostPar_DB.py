import json
import psycopg2
from datetime import date, datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

api_id = ''
api_hash = ""
username = ''

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
    cur.execute("SELECT name from TGDATA")
    rows = cur.fetchall()
    for row in rows:
        channel.append(row[0])
    return channel


def save_data_in_db(message, dates, Messageid, channel_name):
    con = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="abcd0987",
        host="127.0.0.1",
        port="5433")
    cur = con.cursor()
    postgres_insert_query = """INSERT INTO LASTPOST (CHANNEL,ID,POST,DATE) VALUES (%s,%s,%s,%s)"""
    to_insert = (channel_name, Messageid, message, dates)
    cur.execute(postgres_insert_query, to_insert)
    con.commit()
    con.close()


def get_last_post(channel_username):
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    channel_entity = client.get_entity(channel_username)
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
for i in range(len(ch_nm)):
    get_last_post((ch_nm[i]))

