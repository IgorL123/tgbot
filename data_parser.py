import psycopg2
import time
import telethon
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from Bayes import NaiveBayesModel


async def parse(channels, amount_to_parse=180, sleep_period=49, sleep_time=120, update_id=True):
    from config import (API_ID_2, API_HASH_2, USERNAME)
    client = TelegramClient(USERNAME, API_ID_2, API_HASH_2)
    client.start()
    ''' Ограничение примерно в 500 тг каналов '''
    if channels is None:
        print('None')
        return 0
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    for i in range(min(amount_to_parse, len(channels))):
        if i % sleep_period == 0 and i != 0:
            time.sleep(sleep_time)
        cur.execute('SELECT name,last_id from TGCHANNELS2 WHERE name = %s', (channels[i],))
        row = cur.fetchall()
        new_id = last_id = row[0][1]
        limit_to_parse = 100
        if last_id == 0:
            limit_to_parse = 1
        try:
            channel_entity = await client.get_input_entity(channels[i])
            post = await client(GetHistoryRequest(
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
                insert = """INSERT INTO TEMPDATA (POSTID,CHANNEL,ID,POST) VALUES (%s,%s,%s,%s)"""
                to_insert = (0, channels[i], jsnfile['id'], jsnfile['message'])
                cur.execute(insert, to_insert)
                if jsnfile['id'] > new_id:
                    new_id = jsnfile['id']

            con.commit()

        except (ValueError, KeyError, telethon.errors.rpcerrorlist.UsernameNotOccupiedError, TypeError,
                telethon.errors.rpcerrorlist.ChannelPrivateError, telethon.errors.rpcerrorlist.UsernameInvalidError):
            pass
        except telethon.errors.rpcerrorlist.FloodWaitError as e:
            print(e)
            break

        if update_id:
            cur.execute('UPDATE TGCHANNELS2 SET last_id = %s WHERE name = %s', (int(new_id), channels[i],))
            con.commit()

    con.close()


def parse_1(channels, amount_to_parse=180, sleep_period=49, sleep_time=120, update_id=True):
    from config import (API_ID, API_HASH, USERNAME)
    client = TelegramClient(USERNAME, API_ID, API_HASH)
    client.start()
    ''' Ограничение примерно в 500 тг каналов '''
    if channels is None:
        print('None')
        return 0
    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    for i in range(min(amount_to_parse, len(channels))):
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
                insert = """INSERT INTO TEMPDATA (POSTID,CHANNEL,ID,POST) VALUES (%s,%s,%s,%s)"""
                to_insert = (0, channels[i], jsnfile['id'], jsnfile['message'])
                cur.execute(insert, to_insert)
                if jsnfile['id'] > new_id:
                    new_id = jsnfile['id']

            con.commit()

        except (ValueError, KeyError, telethon.errors.rpcerrorlist.UsernameNotOccupiedError, TypeError,
                telethon.errors.rpcerrorlist.ChannelPrivateError, telethon.errors.rpcerrorlist.UsernameInvalidError):
            pass
        except telethon.errors.rpcerrorlist.FloodWaitError as e:
            print(e)
            break

        if update_id:
            cur.execute('UPDATE TGCHANNELS2 SET last_id = %s WHERE name = %s', (int(new_id), channels[i],))
            con.commit()

    con.close()


def madness():
    """
    Make a data
    ch = get_channels()
    parse2(ch, 180, sleep_time=10, update_date=False)
    """
    from database import get_channels
    ch = get_channels(amount_bottom=10, amount_top=390)
    parse_1(ch, amount_to_parse=400, sleep_time=100, update_id=True)


madness()
