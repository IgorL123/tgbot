from telethon.sessions import StringSession
from telethon.sync import TelegramClient, events
import psycopg2
#from config import (API_HASH, API_ID, SOURCE_CHANNEL, SESSION_STRING,TARGET_CHANNEL)



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


#bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
bot = TelegramClient(username, api_id, api_hash)

ch = get_channels()
print(ch)

# Обработчик новых сообщений
@bot.on(events.NewMessage(chats=ch))
async def handler_new_message(event):
    try:
        print(event.raw_text)

        '''database.insert({
            'message_id': event.message.id,
            'mirror_message_id': mirror_message_id
        })'''
    except Exception as e:
        print(e)


if __name__ == '__main__':
    bot.start()
    bot.run_until_disconnected()
