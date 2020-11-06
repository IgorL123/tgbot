import psycopg2
import time
import telethon
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest

api_id = 1999880
api_hash = "0e8b4dc0b4c5fc7ef1d90471f9023e7d"
username = 'redneck88'

client = TelegramClient(username, api_id, api_hash)
client.start()


def get_channels(amount_top=150, amount_bottom=30):
    from datetime import datetime
    now = datetime.today().day
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT date,num_bottom from LASTDATE1")
    rows = cur.fetchall()
    num_of_bottom = 0 if rows[0][1] == (630 - amount_top) // amount_bottom else rows[0][1]
    if rows[0][0] != now:
        cur.execute("UPDATE LASTDATE1 SET date = %s, num_bottom = %s WHERE date = %s", (now, num_of_bottom+1, rows[0][0]))
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


def save_data_in_db(message_id, message, channel_name):
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    insert = """INSERT INTO LASTPOST5 (ID,CHANNEL,POST) VALUES (%s,%s,%s)"""
    to_insert = (channel_name, message_id, message)
    cur.execute(insert, to_insert)
    con.commit()
    con.close()


def get_last_post(channel_username, last_date, id, date=False):
    import datetime
    channel_entity = client.get_input_entity(channel_username)
    date_to_parse = None
    amount_to_parse = 1
    if last_date != '':
        then = last_date[:10].split('-')
        then = datetime.datetime(int(then[0]), int(then[1]), int(then[2]))
        delta = datetime.datetime.now() - then
        if delta.days > 0:
            amount_to_parse = 100
            date_to_parse = then
        else:
            return None

    try:
        post = client(GetHistoryRequest(
            peer=channel_entity,
            limit=amount_to_parse,
            offset_date=date_to_parse,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0))
        messages = post.messages
        last_message = []
        for message in messages:
            last_message.append(message.to_dict())
        index = 0
        for i in range(len(last_message)):
            jsnfile = last_message[i]
            if jsnfile['message'] == '':
                break
            save_data_in_db(id + i, jsnfile['message'], jsnfile['date'], jsnfile['id'], channel_username)
            index = i
        if date:
            return datetime.datetime.now(), id + index
        else:
            return id + index
    except KeyError:
        return KeyError


def parse1(channels, amount_to_parse=180, sleep_period=49, sleep_time=120, update_date=True):

    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    id = 0
    for i in range(min(amount_to_parse, len(channels))):
        id += 1
        if i % sleep_period == 0 and i != 0:
            time.sleep(sleep_time)
        cur.execute('SELECT name,last_save from TGCHANNELS WHERE name = %s', (channels[i],))
        row = cur.fetchall()
        last_save_date = row[0][1]
        try:

            new_data, n_id = get_last_post(channels[i], last_date=last_save_date, id=id, date=True)
            id = n_id
            if update_date:
                if new_data is None:
                    id -= 1
                    continue
                else:
                    cur.execute('UPDATE TGCHANNELS SET last_save = %s WHERE name = %s', (new_data, channels[i],))

        except ValueError or KeyError or telethon.errors.rpcerrorlist.UsernameNotOccupiedError:
            id -= 1
            continue
        except TypeError:
            id -= 1
            continue
        except telethon.errors.rpcerrorlist.ChannelPrivateError:
            id -= 1
            continue

    con.commit()
    con.close()


def parse(channels, amount_to_parse=180, sleep_period=49, sleep_time=120, update_id=True):
    ''' Ограничение примерно в 500 тг каналов '''
    if channels is None:
        print('None')
        return 0
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    for i in range(min(amount_to_parse, len(channels))):
        print(i, ' ', channels[i])
        if i % sleep_period == 0 and i != 0:
            time.sleep(sleep_time)
        cur.execute('SELECT name,last_id from TGCHANNELS2 WHERE name = %s', (channels[i],))
        row = cur.fetchall()
        new_id = last_id = row[0][1]
        limit_to_parse = 100
        if last_id == 0:
            limit_to_parse = 1
        try:
            channel_entity = client.get_input_entity(channels[i])
            post = client(GetHistoryRequest(
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

def madness():
    """ Make a dataset
    ch = get_channels()
    parse2(ch, 180, sleep_time=10, update_date=False) """
    ch = get_channels(amount_bottom=1, amount_top=600)
    print(ch)
    parse(ch, amount_to_parse=500, sleep_time=100)


madness()
