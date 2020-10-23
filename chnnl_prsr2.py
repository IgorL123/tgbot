import requests
from bs4 import BeautifulSoup
import psycopg2


class TgChannels:
    def __init__(self):
        self.url = ''
        self.html = self.get_html()

    def get_html(self):
        try:
            result = requests.get(self.url)
            result.raise_for_status()
            return result.text
        except(requests.RequestException, ValueError):
            print("Server error")
            return False

    def get_channels_tg(self):
        soup = BeautifulSoup(self.html, "html.parser")
        channels_list = soup.findAll('a', class_="channel-item")
        return channels_list


if __name__ == "__main__":
    channels = TgChannels()
    channels = channels.get_channels_tg()

    con = psycopg2.connect(database="postgres", user="postgres", password="abcd0987", host="127.0.0.1", port="5433")
    cur = con.cursor()
    cur.execute("SELECT id,name,count_subs from TGDATAEXTRA")
    rows = cur.fetchall()
    n = rows[-1][0] + 1
    for i in range(n, len(channels) + n):
        x = str(channels[i - n])
        i1 = x.find('"/channel/')
        i2 = x.find('?start=')
        i3 = x.find('<span>')
        i4 = x.find('</span>')
        ch = x[i1 + 10: i2]
        sb = x[i3 + 6: i4]
        postgres_insert_query = """INSERT INTO TGDATAEXTRA (ID,NAME,COUNT_SUBS) VALUES (%s,%s,%s)"""
        cur.execute(postgres_insert_query, (i, ch, sb))

    con.commit()
    con.close()
